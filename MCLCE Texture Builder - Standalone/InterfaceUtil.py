from types import SimpleNamespace as Object

from PySide6.QtWidgets import (
    QWidget
)

def set_font_size(widget: QWidget, size: int) -> None:
    """sets the font size of the widget

    Args:
        widget (QWidget): the widget to set font size on
        size (int): the size of the font
    """

    font = widget.font()
    font.setPointSize(size)
    widget.setFont(font)

def change_margins(
    widget: QWidget, 
    left: int|None = None, 
    top: int|None = None, 
    right: int|None = None, 
    bottom: int|None = None,
    *,
    all: int|None = None
) -> None:
    """change some or all margins of the provided widget

    Args:
        widget (QWidget): the widget to adjust margins
        left (int | None): left margin
        top (int | None): top margin
        right (int | None): right margin
        bottom (int | None): bottom margin
        all (int | None, optional): change all margins at once. Defaults to None.
    """

    # select margins
    new_margins = Object(
        left = None,
        top = None,
        right = None,
        bottom = None
    )
    if all is not None:
        new_margins.left, new_margins.top, new_margins.right, new_margins.bottom = all, all, all, all
    else:
        existing_margins = widget.contentsMargins()
        new_margins.left = left if left is not None else existing_margins.left()
        new_margins.top = top if top is not None else existing_margins.top()
        new_margins.right = right if right is not None else existing_margins.right()
        new_margins.bottom = bottom if bottom is not None else existing_margins.bottom()

    # change margins
    widget.setContentsMargins(
        new_margins.left,
        new_margins.top,
        new_margins.right,
        new_margins.bottom
    )