"""
ViewModelベースクラスのテスト

MVVMパターンにおけるViewModelの基底クラスをテストします。
"""

import pytest
from PyQt6.QtCore import QObject, pyqtSignal


class TestViewModelBase:
    """ViewModelベースクラスの基本機能をテストする"""

    def test_viewmodel_base_exists(self):
        """ViewModelBaseクラスが存在することを確認"""
        from src.viewmodels.base_viewmodel import ViewModelBase

        assert ViewModelBase is not None
        assert issubclass(ViewModelBase, QObject)

    def test_viewmodel_initialization(self):
        """ViewModelが正しく初期化されることを確認"""
        from src.viewmodels.base_viewmodel import ViewModelBase

        vm = ViewModelBase()
        assert vm is not None
        assert isinstance(vm, QObject)

    def test_viewmodel_property_change_notification(self):
        """プロパティ変更時にシグナルが発火することを確認"""
        from src.viewmodels.base_viewmodel import ViewModelBase

        class TestViewModel(ViewModelBase):
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

        vm = TestViewModel()
        signal_received = []

        vm.value_changed.connect(lambda v: signal_received.append(v))
        vm.value = "new_value"

        assert len(signal_received) == 1
        assert signal_received[0] == "new_value"
        assert vm.value == "new_value"

    def test_viewmodel_no_signal_on_same_value(self):
        """同じ値を設定した場合にシグナルが発火しないことを確認"""
        from src.viewmodels.base_viewmodel import ViewModelBase

        class TestViewModel(ViewModelBase):
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

        vm = TestViewModel()
        signal_received = []

        vm.value_changed.connect(lambda v: signal_received.append(v))
        vm.value = "initial"  # 同じ値を設定

        assert len(signal_received) == 0  # シグナルは発火しない
        assert vm.value == "initial"

    def test_viewmodel_multiple_properties(self):
        """複数のプロパティを持つViewModelが正しく動作することを確認"""
        from src.viewmodels.base_viewmodel import ViewModelBase

        class TestViewModel(ViewModelBase):
            name_changed = pyqtSignal(str)
            age_changed = pyqtSignal(int)

            def __init__(self):
                super().__init__()
                self._name = "Alice"
                self._age = 25

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, new_name):
                if self._name != new_name:
                    self._name = new_name
                    self.name_changed.emit(new_name)

            @property
            def age(self):
                return self._age

            @age.setter
            def age(self, new_age):
                if self._age != new_age:
                    self._age = new_age
                    self.age_changed.emit(new_age)

        vm = TestViewModel()
        name_signals = []
        age_signals = []

        vm.name_changed.connect(lambda v: name_signals.append(v))
        vm.age_changed.connect(lambda v: age_signals.append(v))

        vm.name = "Bob"
        vm.age = 30

        assert len(name_signals) == 1
        assert name_signals[0] == "Bob"
        assert len(age_signals) == 1
        assert age_signals[0] == 30
        assert vm.name == "Bob"
        assert vm.age == 30
