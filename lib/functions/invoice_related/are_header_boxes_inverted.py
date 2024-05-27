from lib.functions.utils.get_vertical_line_position import getVerticalLinePosition


def areHeaderMainBoxesInverted(header1, header2):
    header1Sum = getVerticalLinePosition(header1)
    header2Sum = getVerticalLinePosition(header2)

    if header1Sum > header2Sum:
        return True
    else:
        return False
