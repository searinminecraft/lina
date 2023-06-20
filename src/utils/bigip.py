def bigip(x):
    """
    A function to convert big ip's to normal readable ones.
    Thanks to DernisNW for sharing the code!
    """
    return '.'.join([str(y) for y in int.to_bytes(int(x), 4, 'big')])
