"""pytest for shading blocks"""


class TestAddShadingBlock():

    def test_add_shading_block_smoke_test(self, new_idf):
        # type: () -> None
        idf = new_idf
        name = "test"
        height = 7.5
        coordinates = [
            (87.25,24.0),(91.7,25.75),(90.05,30.25),
            (89.55,31.55),(89.15,31.35),(85.1,29.8),
            (86.1,27.2),(84.6,26.65),(85.8,23.5),
            (87.25,24.0)]
        idf.add_shading_block(name, coordinates, height)
