"""
ViewModelベースクラス

MVVMパターンにおけるViewModelの基底クラス。
PyQt6のQObjectを継承し、シグナル/スロット機能を提供します。
"""

from PyQt6.QtCore import QObject


class ViewModelBase(QObject):
    """
    ViewModel基底クラス

    すべてのViewModelはこのクラスを継承します。
    QObjectを継承することで、PyQt6のシグナル/スロット機能を利用できます。

    使用例:
        class MainViewModel(ViewModelBase):
            value_changed = pyqtSignal(str)

            def __init__(self):
                super().__init__()
                self._value = "initial"

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, new_value):
                if self._value != new_value:
                    self._value = new_value
                    self.value_changed.emit(new_value)
    """

    def __init__(self, parent=None):
        """
        ViewModelBaseを初期化

        Args:
            parent (QObject, optional): 親オブジェクト。デフォルトはNone。
        """
        super().__init__(parent)
