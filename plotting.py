def imageSegy(Data):
    """
    imageSegy(Data)
    Image segy Data
    """
    import pylab
    pylab.imshow(Data)
    pylab.title('pymat test')
    pylab.grid(True)
    pylab.show()

def wiggle(Data, SH, skipt=1, maxval=8, lwidth=0.1):
    """
    wiggle(Data, SH)
    """
    import pylab

    t = range(SH['ns'])

    for i in range(0, SH['ntraces'], skipt):

        trace = Data[: , i]
        trace[0] = 0
        trace[SH['ns'] - 1] = 0
        pylab.plot(i + trace / maxval, t, color='black', linewidth=lwidth)
        for a in range(len(trace)):
            if trace[a] < 0:
                trace[a] = 0

        pylab.fill(i + Data[: , i] / maxval, t, 'k', linewidth=0)
    pylab.title(SH['filename'])
    pylab.grid(True)
    pylab.show()

  