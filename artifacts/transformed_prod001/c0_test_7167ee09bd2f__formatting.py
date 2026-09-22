def detector_rotation_matrix(tilt_x, tilt_y, tilt_z):
    r1 = np.array(
        [
            [np.cos(tilt_z), -np.sin(tilt_z), 0],
            [np.sin(tilt_z), np.cos(tilt_z), 0],
            [0, 0, 1],
        ],
        np.float,
    )
    r2 = np.array(
        [
            [np.cos(tilt_y), 0, np.sin(tilt_y)],
            [0, 1, 0],
            [-np.sin(tilt_y), 0, np.cos(tilt_y)],
        ],
        np.float,
    )
    r3 = np.array(
        [
            [1, 0, 0],
            [0, np.cos(tilt_x), -np.sin(tilt_x)],
            [0, np.sin(tilt_x), np.cos(tilt_x)],
        ],
        np.float,
    )
    r2r1 = np.dot(np.dot(r3, r2), r1)
    return r2r1
