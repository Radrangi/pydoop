from streams import DownStreamFilter, UpStreamFilter
from string_utils import quote_string, unquote_string

def toBool(s):
    return s.lower().find('true') > -1



class TextDownStreamFilter(DownStreamFilter):
    """
    Naive textual stream filter implementation.

    It recognizes commands and their parameters expressed as a purely textual
    down_stream flow. 
    
    *NOTE:* this stream filter is intended for debugging purposes only.
    """
    SEP   = '\t'

    CMD_TABLE = {'mapItem'     : ('mapItem', 2, None),
                 'reduceValue' : ('reduceValue', 1, None),
                 'reduceKey'   : ('reduceKey', 1, None),
                 'start'       : ('start', 1, lambda p: [int(p[0]),]),
                 'setJobConf'  : ('setJobConf', None, None),
                 'setInputTypes': ('setInputTypes', 2, None),
                 'runMap' : ('runMap', 3,
                             lambda p: [p[0], int(p[1]), toBool(p[2])]),
                 'runReduce' : ('runReduce', 2,
                                lambda p: [int(p[0]), toBool(p[1])]),
                 'abort' : ('abort', 0, None),
                 'close' : ('close', 0, None),
                 }

    @classmethod
    def convert_message(cls, cmd, args):
        if cmd in cls.CMD_TABLE:
            cmd, nargs, converter = cls.CMD_TABLE[cmd]
            assert nargs is None or len(args) == nargs
            if cmd == 'abort':
                raise ProtocolAbort('received an abort request')
            args = args if converter is None else converter(args)
            return cmd, tuple(args) if args else None
        else:
            raise ProtocolError('Unrecognized command %s' % cmd)

    def __init__(self, stream):
        super(TextDownStreamFilter, self).__init__(stream)

    def next(self):
        line = self.stream.readline()[:-1]
        if len(line) == 0:
            raise StopIteration
        parts = line.split(self.SEP)
        return self.convert_message(parts[0], parts[1:])

class TextUpStreamFilter(UpStreamFilter):
    SEP   = '\t'
    EOL   = '\n'
    def __init__(self, stream):
        super(TextUpStreamFilter, self).__init__(stream)
    def send(self, cmd, *args):
        self.stream.write(cmd)
        for a in args:
            self.stream.write(self.SEP)
            self.stream.write(quote_string(str(a)))
        self.stream.write(self.EOL)
            
