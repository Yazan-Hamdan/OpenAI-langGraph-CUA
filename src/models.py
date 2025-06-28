from typing import List, NotRequired, Union, Literal, TypedDict


class PressKeyCombinationAction(TypedDict):
    type: Literal["press_key_combination"]
    key_combination: str


class EnterTextAction(TypedDict):
    type: Literal["entertext"]
    xpath: str
    text: str


class ClickAction(TypedDict):
    type: Literal["click"]
    xpath: str


class OpenUrlAction(TypedDict):
    type: Literal["openurl"]
    url: str
    inject_element_ids: NotRequired[bool]


class EnterTextAndClickAction(TypedDict):
    type: Literal["enter_text_and_click"]
    text_xpath: str
    click_xpath: str
    text: str


class LoadMhtmlAction(TypedDict):
    type: Literal["load_mhtml"]
    # Additional fields would go here if implemented


class DismissDialogAction(TypedDict):
    type: Literal["dismiss_dialog"]
    selector: str


class InjectElementIdsAction(TypedDict):
    type: Literal["inject_element_ids"]


BrowserAction = Union[
    PressKeyCombinationAction,
    EnterTextAction,
    ClickAction,
    OpenUrlAction,
    EnterTextAndClickAction,
    LoadMhtmlAction,
    DismissDialogAction,
    InjectElementIdsAction,
]

BrowserList = List[BrowserAction]