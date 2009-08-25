class devices:
    def __init__(self):
        pass

    def select_ua(*args, **kwargs):
        return MockDevice()

devices = devices()

class MockDevice:
    def __init__(self):
        self.groups = {
                'mock_group_1': ['mock_attr_1', 'mock_attr_2', 'mock_attr_3'],
                'mock_group_2': ['mock_attr_4', 'mock_attr_5', 'mock_attr_6']
                }

    def __nonzero__(self):
        return True

    def __getattr__(self, name):
        return "Mock device attr %s" % name
    
    
    