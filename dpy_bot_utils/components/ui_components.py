import asyncio
from typing import List, Optional

import discord
from discord import Interaction, TextStyle
from discord.ui import Modal as BaseModal, TextInput as BaseTextInput, View


class Modal(BaseModal):

    def __init__(self,
                 title: str = None,
                 func: callable = None,
                 author: discord.User = None,
                 message: discord.Message = None):
        """
        モーダルウィンドウを生成する
        Args:
            title: モーダルウィンドウのタイトル
            func: モーダルウィンドウが閉じられたときに呼ばれる関数
            author: モーダルウィンドウの作成者
            message: モーダルウィンドウを開いたメッセージ
        """
        super().__init__(title=title)
        self.title = title
        self.func = func
        self.author = author
        self.used = False
        self.message = message
        self.parent_view = None

    def _add_components(self, components: List[BaseTextInput]):
        """
        モーダルウィンドウにコンポーネントを追加する
        Args:
            components: 追加するコンポーネント
        """
        for component in components:
            self.add_item(component)
        return self

    def add_component(self, component: BaseTextInput):
        """
        モーダルウィンドウにコンポーネントを追加する
        Args:
            component: 追加するコンポーネント
        """
        self._add_components([component])
        return self

    def add_components(self, components: List[BaseTextInput]):
        """
        モーダルウィンドウにコンポーネントを追加する
        Args:
            components: 追加するコンポーネント
        """
        self._add_components(components)
        return self

    def on_modal_submit(self, func: callable):
        """
        モーダルウィンドウが閉じられたときに呼ばれる関数を設定する
        Args:
            func: モーダルウィンドウが閉じられたときに呼ばれる関数
        """
        self.func = func
        return self

    def set_title(self, title: str):
        """
        モーダルウィンドウのタイトルを設定する
        Args:
            title: モーダルウィンドウのタイトル
        """
        self.title = title
        return self

    def set_author(self, author: discord.User):
        """
        モーダルウィンドウの作成者を設定する
        Args:
            author: モーダルウィンドウの作成者
        """
        self.author = author
        return self

    def set_message(self, message: discord.Message):
        """
        モーダルウィンドウを開いたメッセージを設定する
        Args:
            message: モーダルウィンドウを開いたメッセージ
        """
        self.message = message
        return self

    def set_used(self, used: bool):
        """
        モーダルウィンドウが使用されたかどうかを設定する
        Args:
            used: モーダルウィンドウが使用されたかどうか
        """
        self.used = used
        return self

    async def on_submit(self, interaction: Interaction):
        """
        モーダルウィンドウが閉じられたときに呼ばれる関数を実行する
        Args:
            interaction: モーダルウィンドウが閉じられたときに呼ばれる関数
        """
        if self.func:
            if asyncio.iscoroutinefunction(self.func):
                await self.func(interaction, self.parent_view, self)
            else:
                self.func(interaction, self.parent_view, self)

    def set_parent_view(self, parent_view: View):
        """
        Viewを設定する
        Args:
            parent_view: View
        """
        self.parent_view = parent_view
        return self

    def set_custom_id(self, custom_id: str):
        """
        モーダルウィンドウのIDを設定する
        Args:
            custom_id: モーダルウィンドウのID
        """
        self.custom_id = custom_id
        return self


class TextInput(BaseTextInput):

    def __init__(self,
                 title: str = None,
                 func: callable = None,
                 style: TextStyle = TextStyle.short,
                 label: Optional[str] = "Input",
                 placeholder: Optional[str] = None,
                 min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
                 required: Optional[bool] = True,
                 pre_fill_value: Optional[str] = None,
                 parent_view: Optional[View] = None
                 ):
        """
        入力値を受け取るTextInputを作成する
        Args:
            title: タイトル
            func: 入力値を受け取る関数
            style: 入力値のスタイル
            label: 入力値のラベル
            placeholder: 入力値のプレースホルダー
            min_length: 最小文字数
            max_length: 最大文字数
            required: 入力値が必須かどうか
            pre_fill_value: 事前に入力する値
        """
        super().__init__(label=label)
        self.parent_view = parent_view
        self.title = title
        self.func = func
        self.style = style
        self.label = label
        self.placeholder = placeholder
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = pre_fill_value
        self.set_parent_view = None

    def set_title(self, title: str):
        """
        タイトルを設定する
        Args:
            title: タイトル
        """
        self.title = title
        return self

    def set_func(self, func: callable):
        """
        入力値を受け取る関数を設定する
        Args:
            func: 入力値を受け取る関数
        """
        self.func = func
        return self

    def set_style(self, style: TextStyle):
        """
        入力値のスタイルを設定する
        Args:
            style: 入力値のスタイル
        """
        self.style = style
        return self

    def set_label(self, label: str):
        """
        入力値のラベルを設定する
        Args:
            label: 入力値のラベル
        """
        self.label = label
        return self

    def set_placeholder(self, placeholder: str):
        """
        入力値のプレースホルダーを設定する
        Args:
            placeholder: 入力値のプレースホルダー
        """
        self.placeholder = placeholder
        return self

    def set_min_length(self, min_length: int):
        """
        最小文字数を設定する
        Args:
            min_length: 最小文字数
        """
        self.min_length = min_length
        return self

    def set_max_length(self, max_length: int):
        """
        最大文字数を設定する
        Args:
            max_length: 最大文字数
        """
        self.max_length = max_length
        return self

    def set_required(self, required: bool):
        """
        入力が必須かどうかを設定する
        Args:
            required: 入力値が必須かどうか
        """
        self.required = required
        return self

    def set_pre_fill_value(self, value: str):
        """
        初期入力値を設定する
        Args:
            value: 入力値
        """
        self.value = value
        return self

    def set_parent_view(self, parent_view: View):
        """
        Viewを設定する
        Args:
            parent_view: View
        """
        self.parent_view = parent_view
        return self
