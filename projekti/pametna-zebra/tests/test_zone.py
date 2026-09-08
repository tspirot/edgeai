from zebra.safety.zone import Polygon, Scene


def test_polygon_contains():
    square = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    assert square.contains((5, 5)) is True
    assert square.contains((15, 5)) is False
    assert square.contains((-1, -1)) is False


def test_degenerate_polygon():
    assert Polygon([(0, 0), (1, 1)]).contains((0.5, 0.5)) is False


def test_scene_where():
    scene = Scene(
        crosswalk=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
        roadway=Polygon([(20, 0), (30, 0), (30, 30), (20, 30)]),
    )
    assert scene.where((5, 5)) == "crosswalk"
    assert scene.where((25, 15)) == "roadway"
    assert scene.where((100, 100)) == "elsewhere"


def test_scene_roundtrip(tmp_path):
    scene = Scene.default(1280, 720)
    path = tmp_path / "zones.json"
    scene.to_file(path)
    loaded = Scene.from_file(path)
    assert loaded.crosswalk.contains(scene.crosswalk.centroid)
    assert loaded.roadway.contains(scene.roadway.centroid)


def test_default_scene_center_is_both():
    scene = Scene.default(1000, 1000)
    # центар слике: у коловозу (вертикална трака) и у прелазу (хоризонтална трака)
    assert scene.roadway.contains((500, 500))
    assert scene.crosswalk.contains((500, 500))
