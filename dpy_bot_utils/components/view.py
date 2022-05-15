import asyncio
from enum import auto
from typing import List, Callable, Any, Union, overload

import discord
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui.button import Button as BaseButton
from discord.ui.select import Select as BaseSelect, SelectOption as BaseSelectOption
from discord.ui.view import View
from discord import ButtonStyle as BaseButtonStyle
from .ui_components import Modal


class ViewGenerator(View):

    def __init__(self,
                 components: List[Union["Button", "Select"]] = None,
                 author: discord.User = None,
                 used: bool = False,
                 message: discord.Message = None,
                 timeout: int = None,
                 used_flag: "ViewUsedBehaviorType" = None,
                 respond_flag: "RespondTargetType" = None,
                 only_one_respond: bool = False,
                 interaction: Interaction = None,
                 bot: commands.Bot = None,
                 prefix: str = None,
                 ):
        """
        :param components: Viewに追加するコンポーネント
        :param author: インタラクションを操作できるユーザー
        :param used: Viewが使用済みかどうか
        :param message: Viewを表示するメッセージ
        :param timeout: Viewを閉じるまでのタイムアウト
        :param used_flag: Viewが使用済みかどうかを判断するフラグ
        :param respond_flag: インタラクションを受け付けるかどうかを判断するフラグ
        :param only_one_respond: 1度だけインタラクションを受け付けるかどうかを判断するフラグ
        """
        super().__init__()
        self.custom_id_prefix = prefix
        if components:
            self._add_components(components=components)
        self.author = author
        self.used = used
        self.message = message
        self.only_one_respond = only_one_respond
        if not used_flag:
            self.used_flag = ViewUsedBehaviorType.NOTHING
        else:
            self.used_flag = used_flag

        if not respond_flag:
            self.respond_flag = RespondTargetType.ONLY_AUTHOR
        else:
            self.respond_flag = respond_flag

        self.timeout = timeout
        self.auto_custom_id = 0
        self.interaction = interaction
        self.bot: commands.Bot = bot

    def set_bot(self, bot: commands.Bot):
        """
        Botオブジェクトを設定する
        :param bot: Botオブジェクト
        """
        self.bot = bot

    def set_interaction(self, interaction: Interaction):
        """
        :protected:
        インタラクションを設定する
        :param interaction: インタラクション
        """
        self.interaction = interaction

    def set_timeout(self, timeout: int):
        """
        Viewを閉じるまでのタイムアウトを設定する
        :param timeout: Viewを閉じるまでのタイムアウト
        """
        self.timeout = timeout
        return self

    def get_auto_custom_id(self) -> str:
        """
        自動生成されるIDを取得する
        """
        _id = self.auto_custom_id
        self.auto_custom_id += 1
        return str(_id)

    def check_author(self, user: discord.User) -> bool:
        """
        インタラクションを受け付ける対象ユーザーかどうかを判断する
        :param user: チェックするユーザー
        """
        if self.author is None:
            return True
        if self.respond_flag == RespondTargetType.ONLY_AUTHOR:
            return user == self.author

    async def interaction_check(self, interaction: Interaction) -> bool:
        """
        インタラクションを受け付けるかどうかを判断する
        :param interaction: チェックするインタラクション
        """
        if not self.check_author(user=interaction.user):
            return False

        if self.only_one_respond and self.used_flag == ViewUsedBehaviorType.VIEW_CLOSE:
            await self.close_view()
            self.used = True
            return True

        if self.only_one_respond and self.used_flag == ViewUsedBehaviorType.DISABLE_ITEMS:
            await self.all_disable()
            self.used = True
            return True

        if self.only_one_respond and self.used_flag == ViewUsedBehaviorType.MESSAGE_DELETE:
            await self.message.delete()
            self.used = True
            return True

        return True

    def _add_components(self, components: List[Union["Button", "Select"]]):
        """
        :protected:
        コンポーネントを追加する
        :param components: Viewに追加するコンポーネント
        """
        def check_generated_custom_id(custom_id: str):
            if len(custom_id) == 32:
                return True
            return False

        for i in components:
            i.set_parent_view(self)
            if not i.url:
                if check_generated_custom_id(i.custom_id) and self.custom_id_prefix:
                    if type(i) == Button:
                        if not i.style == ButtonStyle.link:
                            i.custom_id = f"{self.custom_id_prefix}-{i.custom_id}"
                        else:
                            i.custom_id = None

                    if type(i) == Select:
                        i.custom_id = f"{self.custom_id_prefix}-{i.custom_id}"

                elif not check_generated_custom_id(i.custom_id) and self.custom_id_prefix:
                    if not i.custom_id.startswith(self.custom_id_prefix):
                        i.custom_id = f"{self.custom_id_prefix}-{i.custom_id}"

            self.add_item(item=i)

    def add_components(self, components: List[Union["Button", "Select"]]):
        """
        コンポーネントをリストから追加する
        :param components: Viewに追加するコンポーネント
        """
        self._add_components(components=components)
        return self

    def add_component(self, component: Union["Button", "Select"]):
        """
        コンポーネントを追加する
        :param component: Viewに追加するコンポーネント
        """
        self._add_components(components=[component])
        return self

    def set_author(self, author: discord.User, set_only_author: bool = False):
        """
        インタラクションを操作できるユーザーを設定する
        :param author: インタラクションを操作できるユーザー
        :param set_only_author: インタラクションを対象ユーザーのみが受け付けるかどうかを自動で設定するかどうか
        """
        self.author = author
        if set_only_author:
            self.respond_flag = RespondTargetType.ONLY_AUTHOR
        return self

    def set_used(self, used: bool):
        """
        Viewが使用済みかどうかを設定する
        :param used: Viewが使用済みかどうか
        """
        self.used = used
        return self

    def set_message(self, message: discord.Message):
        """
        Viewを表示するメッセージを設定する
        :param message: Viewを表示するメッセージ
        """
        self.message = message
        return self

    async def all_disable(self, sync_message: bool = True):
        """
        Viewに含まれるすべてのコンポーネントを無効化する
        :param sync_message: Viewを表示するメッセージのコンポーネントを自動で無効化するよう編集するかどうか
        """
        for i in self.children:
            i.disabled = True

        if self.message and sync_message:
            await self.message.edit(view=self)

        elif self.interaction and sync_message:
            await self.interaction.edit_original_message(view=self)

        return self

    async def all_enable(self, sync_message: bool = True):
        """
        Viewに含まれるすべてのコンポーネントを有効化する
        :param sync_message: Viewを表示するメッセージのコンポーネントを自動で有効化するよう編集するかどうか
        """
        for i in self.children:
            i.disabled = False

        if self.message and sync_message:
            await self.message.edit(view=self)

        elif self.interaction and sync_message:
            await self.interaction.edit_original_message(view=self)
        return self

    async def close_view(self, sync_message: bool = True):
        """
        Viewにあるコンポーネントを全て削除する
        :param sync_message: Viewを表示するメッセージのコンポーネントを自動で削除するよう編集するかどうか
        """
        if self.message and sync_message:
            await self.message.edit(view=None)

        elif self.interaction and sync_message:
            await self.interaction.edit_original_message(view=None)
        return self

    async def close_view_and_delete(self, sync_message: bool = True):
        """
        Viewにあるコンポーネントを全て削除してメッセージも削除する
        :param sync_message: Viewを表示するメッセージのコンポーネントを自動で削除するよう編集するかどうか
        """
        if self.message and sync_message:
            await self.message.delete()

        elif self.interaction and sync_message:
            await self.interaction.delete_message()

        return self

    def set_only_one_respond(self, only_one_respond: bool):
        """
        インタラクションを受け付けるユーザーが一人だけかどうかを設定する
        :param only_one_respond: インタラクションを受け付けるユーザーが一人だけかどうか
        """
        self.only_one_respond = only_one_respond
        return self

    def set_used_flag(self, used_flag: "ViewUsedBehaviorType"):
        """
        Viewが使用されたときの挙動を設定する
        :param used_flag: 挙動を示すフラグ
        """
        self.used_flag = used_flag
        return self

    def set_respond_flag(self, respond_flag: "RespondTargetType"):
        """
        Viewに反応する対象を設定する。
        :param ターゲットを示すフラグ
        """
        self.respond_flag = respond_flag
        return self

    async def send_modal(self, modal: Modal):
        """
        Modalを送信します。
        :param 送信するModal
        """
        if self.interaction:
            await self.interaction.response.send_modal(modal)
        return self

    def set_custom_id_prefix(self, prefix: str, sync_components: bool = True):
        """
        IDにPrefixをセットします。
        """
        self.custom_id_prefix = prefix
        if sync_components:
            for i in self.children:
                i.custom_id = f"{prefix}-{i.custom_id}"
        return self


class Button(BaseButton):

    def __init__(self,
                 url: str = None,
                 label: str = None,
                 button_style: "ButtonStyle" = None,
                 func: Callable = None,
                 disabled: bool = False,
                 emoji: str = None,
                 ):
        """
        ボタンを表すクラス
        :param url: ボタンを押したときに開くURL
        :param label: ボタンのラベル
        :param button_style: ボタンのスタイル
        :param func: ボタンを押したときに実行する関数
        :param disabled: ボタンを無効化するかどうか
        :param emoji: ボタンに使用するEmoji
        """
        super().__init__()
        self.url = url
        self.label = label
        self.style = ButtonStyle.primary if not button_style else button_style
        self.func = func
        self.parent_view = None
        self.disabled = disabled
        self.emoji = emoji

    def set_label(self, label: str):
        """
        ボタンのラベルを設定する
        :param label: ボタンのラベル
        """
        self.label = label
        return self

    def set_url(self, url: str):
        """
        ボタンを押したときに開くURLを設定する
        :param url: ボタンを押したときに開くURL
        """
        self.url = url
        self.style = ButtonStyle.link
        self.custom_id = None
        return self

    def set_emoji(self, emoji: str):
        """
        ボタンに使用するEmojiを設定する
        :param emoji: ボタンに使用するEmoji
        """
        self.emoji = emoji
        return self

    def set_style(self, style: discord.ButtonStyle):
        """
        ボタンのスタイルを設定する
        """
        self.style = style
        return self

    def on_click(self, function: Callable[[Interaction, ViewGenerator], Any]):
        """
        ボタンを押したときに実行する関数を設定する
        """
        self.func = function
        return self

    async def callback(self, interaction: Interaction):
        """
        ボタンを押したときに実行する関数を実行する
        """
        if self.func:
            if asyncio.iscoroutinefunction(self.func):
                await self.func(interaction, self.parent_view)
            else:
                self.func(interaction, self.parent_view)

    def set_disabled(self, disabled: bool):
        """
        ボタンを無効化するかどうかを設定する
        """
        self.disabled = disabled
        return self

    def set_parent_view(self, view: View):
        """
        ボタンが属するViewを設定する
        """
        self.parent_view = view
        return self

    def set_custom_id(self, custom_id: str):
        """
        ボタンのカスタムIDを設定する
        """
        self.custom_id = custom_id
        return self


class Select(BaseSelect):

    def __init__(self,
                 placeholder: str = None,
                 options: List[str] = None,
                 disabled: bool = False,
                 func: Callable = None,
                 min_values: int = 1,
                 max_values: int = 1,
                 ):
        """
        セレクターを表すクラス
        :param placeholder: セレクターのプレースホルダー
        :param options: セレクターのオプション
        :param disabled: セレクターを無効化するかどうか
        :param func: セレクターを選択したときに実行する関数
        :param min_values: セレクターの最小選択数
        :param max_values: セレクターの最大選択数
        """
        super().__init__()
        if options:
            self.options = options
        else:
            self.options = []
        self.placeholder = placeholder
        self.disabled = disabled
        self.parent_view = None
        self.event_handlers = {}
        self.func = func
        self.trigger_type = SelectTriggerType.ALWAYS
        self.min_values = min_values
        self.max_values = max_values

    def add_option(self, option: "SelectOption", **kwargs):
        """
        セレクターのオプションを追加する
        :param option: セレクターのオプション
        """
        self.options.append(option)
        if option.func:
            self.event_handlers[option.value] = option.func
        else:
            self.event_handlers[option.value] = None
        return self

    def add_options(self, options: List["SelectOption"]):
        """
        セレクターのオプションを一括で追加する
        :param options: セレクターのオプション
        """
        for i in options:
            self.add_option(option=i)
        return self

    def set_placeholder(self, placeholder: str):
        """
        セレクターのプレースホルダーを設定する
        :param placeholder: セレクターのプレースホルダー
        """
        self.placeholder = placeholder
        return self

    def set_parent_view(self, view: View):
        """
        セレクターが属するViewを設定する
        :param view: セレクターが属するView
        """
        self.parent_view = view
        return self

    def set_disabled(self, disabled: bool):
        """
        セレクターを無効化するかどうかを設定する
        :param disabled: セレクターを無効化するかどうか
        """
        self.disabled = disabled
        return self

    def on_select(self, function: Callable[[Interaction, ViewGenerator], Any]):
        """
        セレクターを選択したときに実行する関数を設定する
        :param function: セレクターを選択したときに実行する関数
        """
        self.func = function
        return self

    async def callback(self, interaction: Interaction):
        """
        セレクターを選択したときに実行する関数を実行する
        """
        try:
            if self.func:
                if self.trigger_type == SelectTriggerType.ALWAYS:
                    if asyncio.iscoroutinefunction(self.func):
                        await self.func(interaction, self.parent_view)
                    else:
                        self.func(interaction, self.parent_view)

                elif self.trigger_type == SelectTriggerType.MIN_AND_MAX and self.min_values == len(
                        self.values) == self.max_values:
                    if asyncio.iscoroutinefunction(self.func):
                        await self.func(interaction, self.parent_view)
                    else:
                        self.func(interaction, self.parent_view)

                elif self.trigger_type == SelectTriggerType.ONLY_MAX and self.max_values == len(
                        self.values):
                    if asyncio.iscoroutinefunction(self.func):
                        await self.func(interaction, self.parent_view)
                    else:
                        self.func(interaction, self.parent_view)

            event_func = self.event_handlers[self.values[len(self.values) - 1]]
            if event_func:
                if asyncio.iscoroutinefunction(event_func):
                    await event_func(interaction, self.parent_view)
                else:
                    event_func(interaction, self.parent_view)
        except Exception as e:
            print(e)

    def set_min_values(self, min_values: int):
        """
        セレクターの最小選択数を設定する
        """
        self.min_values = min_values
        return self

    def set_max_values(self, max_values: int):
        """
        セレクターの最大選択数を設定する
        """
        self.max_values = max_values
        return self


class SelectOption(BaseSelectOption):

    def __init__(self,
                 label: str = None,
                 value: str = None,
                 func: Callable[[Interaction, ViewGenerator], Any] = None,
                 description: str = None,
                 default: bool = False
                 ):
        """
        セレクターのオプションを表すクラス
        :param label: セレクターのオプションのラベル
        :param value: セレクターのオプションの値
        :param func: セレクターのオプションを選択したときに実行する関数
        :param description: セレクターのオプションの説明
        :param default: セレクターのオプションがデフォルトで選択されているかどうか
        """
        super().__init__(label=label)
        self.label = label
        if not value:
            self.value = value
        else:
            self.value = label
        self.parent_view = None
        self.description = description
        self.func = func
        self.default = default

    def set_label(self, label: str):
        """
        セレクターのオプションのラベルを設定する
        :param label: セレクターのオプションのラベル
        """
        self.label = label
        return self

    def set_value(self, value: str):
        """
        セレクターのオプションの値を設定する
        :param value: セレクターのオプションの値
        """
        self.value = value
        return self

    def set_description(self, description: str):
        """
        セレクターのオプションの説明を設定する
        """
        self.description = description
        return self

    def set_parent_view(self, view: View):
        """
        セレクターのオプションが属するViewを設定する
        :param view: セレクターのオプションが属するView
        """
        self.parent_view = view

    def on_select(self, function: Callable[[Interaction, ViewGenerator], Any]):
        """
        セレクターのオプションを選択したときに実行する関数を設定する
        :param function: セレクターのオプションを選択したときに実行する関数
        """
        self.func = function
        return self

    def set_default(self, default: bool):
        """
        セレクターのオプションがデフォルトで選択されるかどうかを設定する
        """
        self.default = default
        return self

    def set_func(self, func: Callable[[Interaction, ViewGenerator], Any]):
        """
        セレクターのオプションを選択したときに実行する関数を設定する
        :param func: セレクターのオプションを選択したときに実行する関数
        """
        self.func = func
        return self


class SelectTriggerType:
    """
    セレクターのトリガータイプ
    """
    ALWAYS = auto()
    ONLY_MAX = auto()
    MIN_AND_MAX = auto()


class ViewUsedBehaviorType:
    """
    Viewの使用方法
    """
    VIEW_CLOSE = auto()
    MESSAGE_DELETE = auto()
    NOTHING = auto()
    DISABLE_ITEMS = auto()


class RespondTargetType:
    """
    レスポンスするターゲットタイプ
    """
    ONLY_AUTHOR = auto()
    ALL_USERS = auto()


class ComponentsUtils:
    """
    Componentsを扱いやすくするための補助関数群
    """

    @staticmethod
    def get_view_children(view: View):
        """
        Viewの子クラスを取得する
        params:
        view: 取得したいView
        index: 取得したいIndex
        """
        return view.children

    @staticmethod
    def get_view_children_value(view: View, index: int = 0):
        """
        Viewの子クラスの値を取得する
        params:
        view: 取得したいView
        index: 取得したいIndex
        """
        try:
            return view.children[index].values
        except IndexError:
            raise IndexError("Viewの子クラスが存在しません")

    @staticmethod
    def get_modal_children(modal: Modal):
        """
        Modalの小クラスを取得する
        params:
        modal: 取得したいmodal
        """
        return modal.children

    @staticmethod
    def get_modal_children_value(modal: Modal, index: int = 0):
        """
        Modalの子クラスの値を取得する
        params:
        modal: 取得したいmodal
        index: 取得したいIndex
        """
        try:
            return modal.children[index].value
        except IndexError:
            raise IndexError("Viewの子クラスが存在しません")


class ButtonStyle(BaseButtonStyle):
    pass
