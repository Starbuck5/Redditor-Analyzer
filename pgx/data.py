class data:
    _resolution = False

    @staticmethod
    def get_resolution():
        if data._resolution:
            return data._resolution.copy()
        raise SyntaxError("pgx not initialized")

    @staticmethod
    def set_resolution(res):
        data._resolution = res.copy()

    _internalpath = False

    @staticmethod
    def get_internalpath():
        if data._internalpath == False:
            raise SyntaxError("pgx not initialized")
        return data._internalpath

    _projectpath = False

    @staticmethod
    def get_projectpath():
        if data._projectpath == False:
            raise SyntaxError("pgx not initialized")
        return data._projectpath

    _scale = 1

    @staticmethod
    def get_global_scale():
        return data._scale

    @staticmethod
    def set_global_scale(scale):
        if scale <= 0.05:
            raise ValueError("pgx global scale has to be greater than 0.05")
        data._scale = scale

    _offset = [0, 0]

    @staticmethod
    def get_global_offset():
        return data._offset

    @staticmethod
    def set_global_offset(offset):
        data._offset = list(offset).copy()

    _scaling_mode = "manual"
