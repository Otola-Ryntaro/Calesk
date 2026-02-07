"""
週間カレンダーの重複イベント配置テスト

_calculate_event_positions と _is_overlapping メソッドの
正確な動作を検証する。特に重複イベント発生時に
全てのイベントの幅と位置が正しく再計算されることを確認する。
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.models.event import CalendarEvent
from src.image_generator import ImageGenerator


def _make_event(
    event_id: str,
    summary: str,
    start_hour: int,
    start_min: int,
    end_hour: int,
    end_min: int,
    date: datetime = None,
    is_all_day: bool = False,
    color_id: str = "1"
) -> CalendarEvent:
    """テスト用イベントを生成するヘルパー"""
    base_date = date or datetime(2026, 2, 5)
    return CalendarEvent(
        id=event_id,
        summary=summary,
        start_datetime=base_date.replace(hour=start_hour, minute=start_min),
        end_datetime=base_date.replace(hour=end_hour, minute=end_min),
        is_all_day=is_all_day,
        calendar_id="primary",
        color_id=color_id
    )


@pytest.fixture
def generator():
    """ImageGeneratorインスタンスを生成するフィクスチャ"""
    with patch('src.image_generator.AUTO_DETECT_RESOLUTION', False):
        gen = ImageGenerator()
    return gen


class TestIsOverlapping:
    """_is_overlapping メソッドのテスト"""

    def test_non_overlapping_events(self, generator):
        """重複しないイベント（AがBの前に終わる）"""
        event_a = _make_event("1", "A", 9, 0, 10, 0)
        event_b = _make_event("2", "B", 10, 0, 11, 0)
        assert generator._is_overlapping(event_a, event_b) is False

    def test_overlapping_events(self, generator):
        """部分的に重複するイベント"""
        event_a = _make_event("1", "A", 9, 0, 10, 30)
        event_b = _make_event("2", "B", 10, 0, 11, 0)
        assert generator._is_overlapping(event_a, event_b) is True

    def test_fully_contained_event(self, generator):
        """一方が他方に完全に含まれるイベント"""
        event_a = _make_event("1", "A", 9, 0, 12, 0)
        event_b = _make_event("2", "B", 10, 0, 11, 0)
        assert generator._is_overlapping(event_a, event_b) is True

    def test_same_time_events(self, generator):
        """完全に同じ時間のイベント"""
        event_a = _make_event("1", "A", 10, 0, 11, 0)
        event_b = _make_event("2", "B", 10, 0, 11, 0)
        assert generator._is_overlapping(event_a, event_b) is True

    def test_adjacent_events_not_overlapping(self, generator):
        """隣接するイベント（Aの終了=Bの開始）は重複しない"""
        event_a = _make_event("1", "A", 9, 0, 10, 0)
        event_b = _make_event("2", "B", 10, 0, 11, 0)
        # start < end かつ start < end のため、10 < 10 は False
        assert generator._is_overlapping(event_a, event_b) is False


class TestCalculateEventPositionsSingleEvent:
    """単一イベントの配置テスト"""

    def test_single_event_full_width(self, generator):
        """イベントが1つだけの場合、列幅いっぱいに配置される"""
        events = [_make_event("1", "A", 10, 0, 11, 0)]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 1
        assert positions[0]['column'] == 0
        assert positions[0]['width'] == column_width
        assert positions[0]['x_offset'] == 0


class TestCalculateEventPositionsTwoOverlapping:
    """2つの重複イベントの配置テスト"""

    def test_two_overlapping_events_equal_width(self, generator):
        """
        2つの重複イベントがある場合、
        両方とも幅が column_width / 2 になるべき。

        これが現状のバグ: 最初のイベントはfull幅で配置され、
        2つ目が追加されても再計算されない。
        """
        events = [
            _make_event("1", "A", 10, 0, 11, 0),
            _make_event("2", "B", 10, 0, 11, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 2

        # 両方の幅が均等であること（column_width / 2 = 60）
        expected_width = column_width // 2
        for pos in positions:
            assert pos['width'] == expected_width, (
                f"イベント '{pos['event'].summary}' の幅が {pos['width']} "
                f"ですが、期待値は {expected_width} です"
            )

        # 列0と列1にそれぞれ配置されること
        columns = sorted(p['column'] for p in positions)
        assert columns == [0, 1]

        # x_offsetが正しいこと
        for pos in positions:
            assert pos['x_offset'] == pos['column'] * expected_width

    def test_two_non_overlapping_events_full_width(self, generator):
        """
        2つの重複しないイベントは、それぞれfull幅で配置される
        """
        events = [
            _make_event("1", "A", 9, 0, 10, 0),
            _make_event("2", "B", 11, 0, 12, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 2
        for pos in positions:
            assert pos['width'] == column_width
            assert pos['column'] == 0
            assert pos['x_offset'] == 0


class TestCalculateEventPositionsThreeOverlapping:
    """3つの重複イベントの配置テスト"""

    def test_three_overlapping_events_equal_width(self, generator):
        """
        3つの重複イベントがある場合、
        全て幅が column_width / 3 になるべき。
        """
        events = [
            _make_event("1", "A", 10, 0, 11, 0),
            _make_event("2", "B", 10, 0, 11, 0),
            _make_event("3", "C", 10, 0, 11, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 3

        # 全ての幅が均等であること（column_width / 3 = 40）
        expected_width = column_width // 3
        for pos in positions:
            assert pos['width'] == expected_width, (
                f"イベント '{pos['event'].summary}' の幅が {pos['width']} "
                f"ですが、期待値は {expected_width} です"
            )

        # 列0, 1, 2にそれぞれ配置されること
        columns = sorted(p['column'] for p in positions)
        assert columns == [0, 1, 2]

        # x_offsetが正しいこと
        for pos in positions:
            assert pos['x_offset'] == pos['column'] * expected_width

    def test_partial_overlap_three_events(self, generator):
        """
        A: 10:00-11:00
        B: 10:30-11:30
        C: 11:00-12:00

        AとBは重複、BとCは重複、AとCは重複しない。
        この場合、AとBは同じグループ（最大2列）、
        BとCも同じグループ（最大2列）。
        全体として最大2列のグループが存在する。

        AとBの区間では2列配置、
        BとCの区間でも2列配置になるべき。
        """
        events = [
            _make_event("1", "A", 10, 0, 11, 0),
            _make_event("2", "B", 10, 30, 11, 30),
            _make_event("3", "C", 11, 0, 12, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 3

        # イベントを名前で検索
        pos_map = {p['event'].summary: p for p in positions}

        # A と B は重複 -> 同じグループで2列
        # 幅は column_width / 2 = 60
        expected_width_ab = column_width // 2
        assert pos_map['A']['width'] == expected_width_ab
        assert pos_map['B']['width'] == expected_width_ab

        # A と B は異なる列に配置されること
        assert pos_map['A']['column'] != pos_map['B']['column']


class TestCalculateEventPositionsComplexOverlap:
    """複雑な重複パターンのテスト"""

    def test_chain_overlap(self, generator):
        """
        連鎖的な重複:
        A: 10:00-11:00
        B: 10:30-11:30
        C: 11:00-12:00
        D: 13:00-14:00 (独立)

        A-B が重複、B-C が重複、D は独立。
        """
        events = [
            _make_event("1", "A", 10, 0, 11, 0),
            _make_event("2", "B", 10, 30, 11, 30),
            _make_event("3", "C", 11, 0, 12, 0),
            _make_event("4", "D", 13, 0, 14, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 4

        pos_map = {p['event'].summary: p for p in positions}

        # D は独立 -> full幅
        assert pos_map['D']['width'] == column_width
        assert pos_map['D']['column'] == 0

    def test_four_simultaneous_events(self, generator):
        """
        4つの完全に同時刻のイベント。
        全て column_width / 4 の幅であるべき。
        """
        events = [
            _make_event("1", "A", 10, 0, 11, 0),
            _make_event("2", "B", 10, 0, 11, 0),
            _make_event("3", "C", 10, 0, 11, 0),
            _make_event("4", "D", 10, 0, 11, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 4

        expected_width = column_width // 4
        for pos in positions:
            assert pos['width'] == expected_width, (
                f"イベント '{pos['event'].summary}' の幅が {pos['width']} "
                f"ですが、期待値は {expected_width} です"
            )

        # 全て異なる列に配置されること
        columns = sorted(p['column'] for p in positions)
        assert columns == [0, 1, 2, 3]

    def test_mixed_overlap_groups(self, generator):
        """
        グループ1: A(10-11), B(10-11) -> 2列
        グループ2: C(14-15), D(14-15), E(14-15) -> 3列

        各グループ内で正しい幅が計算されること。
        """
        events = [
            _make_event("1", "A", 10, 0, 11, 0),
            _make_event("2", "B", 10, 0, 11, 0),
            _make_event("3", "C", 14, 0, 15, 0),
            _make_event("4", "D", 14, 0, 15, 0),
            _make_event("5", "E", 14, 0, 15, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 5

        pos_map = {p['event'].summary: p for p in positions}

        # グループ1: A, B -> 幅 = 120 / 2 = 60
        assert pos_map['A']['width'] == 60
        assert pos_map['B']['width'] == 60

        # グループ2: C, D, E -> 幅 = 120 / 3 = 40
        assert pos_map['C']['width'] == 40
        assert pos_map['D']['width'] == 40
        assert pos_map['E']['width'] == 40


class TestCalculateEventPositionsEdgeCases:
    """エッジケースのテスト"""

    def test_empty_events_list(self, generator):
        """空のイベントリストの場合"""
        positions = generator._calculate_event_positions([], 120)
        assert positions == []

    def test_event_ordering_preserved(self, generator):
        """イベントが開始時刻順にソートされて配置されること"""
        events = [
            _make_event("2", "B", 11, 0, 12, 0),
            _make_event("1", "A", 10, 0, 11, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        # 開始時刻順にソートされていること
        assert positions[0]['event'].summary == "A"
        assert positions[1]['event'].summary == "B"

    def test_different_duration_overlapping_events(self, generator):
        """
        異なる長さの重複イベント:
        A: 10:00-12:00 (2時間)
        B: 10:00-10:30 (30分)
        C: 11:30-12:30 (1時間)

        AとBは重複、AとCは重複、BとCは重複しない。
        A, B, C は連結グループ。
        """
        events = [
            _make_event("1", "A", 10, 0, 12, 0),
            _make_event("2", "B", 10, 0, 10, 30),
            _make_event("3", "C", 11, 30, 12, 30),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        assert len(positions) == 3

        pos_map = {p['event'].summary: p for p in positions}

        # A, B は重複 -> 同じグループ
        assert pos_map['A']['column'] != pos_map['B']['column']

        # A, C は重複 -> 同じグループ
        assert pos_map['A']['column'] != pos_map['C']['column']

        # B, C は重複しないので同じ列に配置可能
        # -> B: 列1(or 適切な列), C: 列1(Bと同じ列で可)

    def test_no_overlap_between_x_positions(self, generator):
        """
        配置結果のX座標範囲が重複しないことを検証。
        同一時間帯の複数イベントのブロックが重ならないこと。
        """
        events = [
            _make_event("1", "A", 10, 0, 11, 0),
            _make_event("2", "B", 10, 0, 11, 0),
            _make_event("3", "C", 10, 0, 11, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        # 各イベントのX座標範囲が重複しないこと
        for i, pos_a in enumerate(positions):
            for j, pos_b in enumerate(positions):
                if i >= j:
                    continue
                a_start = pos_a['x_offset']
                a_end = pos_a['x_offset'] + pos_a['width']
                b_start = pos_b['x_offset']
                b_end = pos_b['x_offset'] + pos_b['width']
                # 範囲が重複しないことを確認
                assert a_end <= b_start or b_end <= a_start, (
                    f"イベント '{pos_a['event'].summary}' ({a_start}-{a_end}) と "
                    f"'{pos_b['event'].summary}' ({b_start}-{b_end}) のX座標が重複"
                )

    def test_all_positions_within_column_width(self, generator):
        """全てのイベントブロックがcolumn_width内に収まること"""
        events = [
            _make_event("1", "A", 10, 0, 11, 0),
            _make_event("2", "B", 10, 0, 11, 0),
            _make_event("3", "C", 10, 0, 11, 0),
            _make_event("4", "D", 10, 0, 11, 0),
        ]
        column_width = 120

        positions = generator._calculate_event_positions(events, column_width)

        for pos in positions:
            assert pos['x_offset'] >= 0, (
                f"イベント '{pos['event'].summary}' のx_offsetが負: {pos['x_offset']}"
            )
            assert pos['x_offset'] + pos['width'] <= column_width, (
                f"イベント '{pos['event'].summary}' がcolumn_widthを超えています: "
                f"x_offset={pos['x_offset']}, width={pos['width']}, "
                f"合計={pos['x_offset'] + pos['width']}, 列幅={column_width}"
            )
