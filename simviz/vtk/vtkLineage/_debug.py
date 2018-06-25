import vtk, os, logging, datetime, textwrap

class vtkStreamHandler(logging.StreamHandler):

    """
    vtkStreamHandler

    A vtk wrapper for the logging.StreamHandler to allow for printing of console output to a vtk window.
    """

    _level_color = {
        'DEBUG': [0.8, 0.8, 0.8],
        'INFO': [1.0, 1.0, 1.0],
        'WARNING': [0.9, 0.8, 0.4],
        'ERROR': [1.0, 0.3, 0.3],
        'CRITICAL': [1.0, 0.0, 0.0 ]
    }

    _font = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir, 'assets', 'fonts', 'LiberationMono-Regular.ttf'))

    def __init__(self, renderer, interactor, level=logging.INFO):
        self._renderer = renderer
        self._renderer.AddObserver('EndEvent', self.update)
        self._interactor = interactor
        logging.StreamHandler.__init__(self)

        self.text_timeout = 10 # [seconds]
        self.text_fadetime = 1 # [seconds]
        self.rows = 1

        self.fontsize = 14
        self.position = [0, 0]

        self.textActors = []
        self.initializeTextActors()

        self.setLevel(level)
        logging.getLogger().addHandler(self)

    def initializeTextActors(self):
        self.textActors = []
        for i in range(self.rows):
            self.textActors.append({
                'actor': vtk.vtkTextActor(),
                'last_update': datetime.datetime.now(),
                })
            self.formatTextActor(self.textActors[-1]['actor'])
            self._renderer.AddActor2D(self.textActors[-1]['actor'])
        self.repositionTextActors()

    def update(self, obj, event):
        for i in range(self.rows):
            delta = datetime.datetime.now() - self.textActors[i]['last_update']
            opacity = 0 if delta.days > 0 else \
                      min(1, max(0, 1 - ((delta.seconds + delta.microseconds * 0.000001) - self.text_timeout) / self.text_fadetime))
            self.textActors[i]['actor'].GetTextProperty().SetOpacity(opacity * 1.0)
            self.textActors[i]['actor'].GetTextProperty().SetBackgroundOpacity(opacity * 0.5)

    def formatTextActor(self, textActor, color=[1,1,1], bg_color=[0,0,0]):
        textActor.GetTextProperty().SetFontFamilyToCourier()
        textActor.GetTextProperty().SetColor(*color)
        textActor.GetTextProperty().SetBackgroundColor(*bg_color)
        textActor.GetTextProperty().SetBackgroundOpacity(0.5)
        textActor.GetTextProperty().SetOpacity(0)
        textActor.GetTextProperty().SetLineSpacing(0.0)
        textActor.GetTextProperty().SetBold(1)
        textActor.GetTextProperty().SetFontFile(self._font)
        textActor.ComputeScaledFont(self._renderer)

    def repositionTextActors(self):
        for i in range(self.rows):
            self.textActors[i]['actor'].GetTextProperty().SetFontSize(self.fontsize)
            self.textActors[i]['actor'].SetDisplayPosition(self.position[0], self.position[1]+int(self.fontsize*i*1.4))

    def printLine(self, text, level='DEBUG'):
        """
        Print a line to the array of vtkTextActors contained within the vtkStreamHandler
        """
        self.textActors.insert(0, self.textActors.pop())
        self.textActors[0]['actor'].GetTextProperty().SetColor(*self._level_color[level])
        self.textActors[0]['actor'].SetInput(text)
        self.textActors[0]['last_update'] = datetime.datetime.now()
        self.repositionTextActors()

    def emit(self, record, char_limit=100):
        """
        Overload the logging.StreamHandler emit function to introduce line breaks and format the line with the internal printLine function

        Args:
            record:     The string to output
            char_limit: The line character limit for the vtkTextActors
        """
        for s in str(self.format(record)).split('\n'):
            for s in textwrap.wrap(s, char_limit):
                self.printLine(s.ljust(char_limit), level=record.levelname)
