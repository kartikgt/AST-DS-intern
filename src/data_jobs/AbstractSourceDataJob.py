
class AbstractSourceDataJob():
    # TODO Is this the best interface? Open to suggestions
    def get_data(self):
        raise NotImplementedError()
    
    def clean_data(self):
        raise NotImplementedError()
    
    def save_data(self):
        raise NotImplementedError()



