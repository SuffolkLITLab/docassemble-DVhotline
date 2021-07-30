from mechanize import Browser
def search(inputName, inputType):
  br = Browser()    
  br.open("https://findhelp.janedoe.org/find_help/search")  
  br.select_form(id="searchprograms")  
  
  if inputType == 'city':
	  br["city"] = [inputName]  
  elif inputType == 'zip':
	  br["zip"] = inputName
  else:
    raise Exception("You must enter a valid city name or zip code")
	
  response = br.submit()  
  cleanResponse = response.read().decode("utf-8") #get rid of bytes-type error and white spaces
  return cleanResponse

#parse the output with HTMLParser
from html.parser import HTMLParser
class HTMLFilter(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.recording = 0
    self.data = []
    self.link = ""

  def handle_starttag(self, tag, attributes):    
    if tag != 'div' and tag != 'a':
      return
    for name, value in attributes:
      if name == 'class' and value == 'article':
        self.recording += 1
    
    #Preserve links
    if tag == 'a':      
      for attr in attributes:
        if attr[0]=='href' and str(attr[1]).startswith('http'):
          self.link = '](' + attr[1] + ')';
          self.data.append('[');
    
  def handle_endtag(self, tag):
    if tag == 'div' and self.recording:
      self.recording -= 1
	  #Attach links
    if tag == 'a':
      self.data.append(self.link);

  def handle_data(self, data):    
    if self.recording: 
      self.data.append(data);   
      
#Search then parse      
def ma_dv_hotline(inputName: str, inputType: str):
  searchResults = search(inputName, inputType)
  f = HTMLFilter()
  f.feed(searchResults)  
  Results = f.data
  clearnResults = [item.replace('\n','').replace('\t','') for item in Results]
  return clearnResults
      
