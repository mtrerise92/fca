"""First_Class_Analyzer.
A Text Analyzer class that can analyze text from different sources, including URLs and file paths. 
NOTE: On lines containing `with open` and `path` under Content Sources, update the path to match the file location on your computer. Additionally, `encoding='utf-8'` is used when reading from a file, to ensure proper handling of text. This may or may not be needed on your system."""
   
# Modules.
from collections import Counter
import string
import re
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

#########################

# Analyzer class.
class Analyzer:
    """A class for analyzing different types of text."""

    def __init__(self, src, orig_content=None, src_type='text'):
        """Initialize the Analyzer object with content source and source type."""  
        self.src = src
        self.src_type = src_type
        self._src_type = src_type
        self._content = None
        self._orig_content = orig_content if orig_content is not None else src

        if self.src_type == 'discover':
            if src.startswith('http'):
                self._src_type = 'url'
            elif src.endswith('.txt') or '/' in src or '\\' in src:
                self._src_type = 'path'
            else:
                self._src_type = 'text'

        if self._src_type == 'url':
            self._content = self._fetch_from_url(src)
        elif self._src_type == 'path':
            self._content = self._read_from_file(src)
        elif self._src_type == 'text':
            self._content = src
        else:
            raise ValueError(f'Unsupported source type: {self._src_type}')
                            
        self._orig_content = self._content
        self.text = 'text'

    def _fetch_from_url(self, url):
        """Get content from a given URL."""
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    
    def _read_from_file(self, file_path):
        """Read content from a given file path."""
        with open(file_path, 'r', encoding='utf-8') as file: 
            return file.read()
        
    def set_content_to_tag(self, tag, tag_id):
        """Set the content of the text within an HTML document.
        
        Keyword arguments:
            tag (str) - HTML tag to read
            tag_id (str) - id attribute for the tag, default None
            """
        soup = BeautifulSoup(self._original_content, 'html.parser')
        element = soup.find('tag', 'id=tag_id')
        if element:
            self._content = element.get_text(strip=True)
        else:
            self._content = ""

    def reset_content(self) -> str:
        """Reset the content to its original state."""
        self._content = self._orig_content
        return self._content
    
    def _words(self, casesensitive=False):
        """Generate a list of words from the text content."""
        if self._content is None:
            return None

        words = self._orig_content.split()
        if not casesensitive:
            words = [word.strip(string.punctuation).lower() for word in words]
        else:
            words = [word.strip(string.punctuation) for word in words]
        return words

    def common_words(self, minlen=1, maxlen=100, count=10, casesensitive=False):
        """Return a list of the most common words in the text content.
        
        Keyword arguments:
        minlen (int) - Minimum length of words to consider. Default is 1.
        maxlen (int) - Maximum length of words to consider. Default is 100.
        count (int) - Number of most common words to return. Default is 10.
        casesensitive (bool) - Case sensitive comparison. Default is False.
        """
        if self._src_type == 'text':
            words = self._words(casesensitive=False)
            filtered_words = [word for word in words if minlen <= len(word) <= maxlen]
            word_counts = Counter(filtered_words)
            most_common_words = word_counts.most_common(count)
            return [(word.upper(), freq) for word, freq in most_common_words]

        if self._src_type == 'path':
            words = self._words(casesensitive=False)
            filtered_words = [word for word in words if minlen <= len(word) <= maxlen]
            word_counts = Counter(filtered_words)
            most_common_words = word_counts.most_common(count)
            return [(word.upper(), freq) for word, freq in most_common_words]

        return None

    def char_distribution(self, casesensitive=False, letters_only=False):
        """Return a list of the distribution of characters sorted by number in descending order."""
        if self._src_type == 'text':
            content = self._orig_content if casesensitive else self._orig_content.lower()
            char_counts = Counter(char for char in content if not letters_only or char.isalpha())
            sorted_char_counts = sorted(char_counts.items(), key=lambda item: item[1], reverse=True)
            return sorted_char_counts

        if self._src_type == 'path':
            content = self._read_from_file(self.src)
            content = content if casesensitive else content.lower()
            char_counts = Counter(char for char in content if letters_only or char.isalpha())
            sorted_char_counts = sorted(char_counts.items(), key=lambda item:[1], reverse=True)
            return sorted_char_counts

        return None

    def plot_common_words(self, minlen=1, maxlen=100, count=10, casesensitive=False):
        """Plot the most common words in the text.
    
        Keyword arguments:
        minlen (int) - minimum length of words, default is 1
        maxlen (int) - maximum length of words, default is 100
        count (int) - number of most common words to return, default is 10
        casesensitive (bool) - case sensitive comparison, default False
        """
        common_words = self.common_words(minlen, maxlen, count, casesensitive=False)
        if common_words:
            words, counts = zip(*common_words)
            plt.bar(words, counts)
            plt.xlabel('Words')
            plt.ylabel('Count')
            plt.title('Most Common Words')
            plt.show()
        else:
            print("No content available to plot.")

    def plot_char_distribution(self, casesensitive=False, letters_only=False):
        """Plot the distribution of characters in the text.
    
        Keyword arguments:
        casesensitive (bool) - case sensitive comparison, default False
        letters_only (bool) - only count letters, default False
        """
        char_distribution = self.char_distribution(casesensitive=False, letters_only=False)
        if char_distribution:
            chars, counts = zip(*char_distribution)
            plt.bar(chars, counts)
            plt.xlabel('Characters')
            plt.ylabel('Frequency')
            plt.title('Character Distribution')
            plt.show()
        else:
            print("No content available to plot.")
    
    def _distinct_word_count(self, casesensitive=True):
        """Return the number of distinct words in the text"""
        words = re.findall(r'\b\w+\b', self._content)
        if not casesensitive:
            words = [word.lower() for word in words]
        return len(set(words))


    @property
    def avg_word_length(self) -> float:
        """Return the average word length in the text rounded to the nearest hundredth."""
        if self._src_type == 'text':
            self._content = self._orig_content
            words = self._words(casesensitive=False)
            if words:
                avg_length = sum(len(word) for word in words) / len(words)
                return round(avg_length, 2)
        
        if self._src_type == 'path':
            words = self._words(casesensitive=False)
            if words:
                avg_length = sum(len(words) for words in words) / len(words)
                return round(avg_length, 2)
            
        return 0.0
    
    @property
    def word_count(self):
        """Return the number of words in the text."""
        if self._src_type == 'text':
            self._content = self._orig_content
            return len(self._words())
    
        if self._src_type == 'path':
            self._content = self._read_from_file(self.src)
            return len(self._words())
    
        if self._src_type == 'url':
            self._content = self._fetch_from_url(self.src)
            return len(self._words())
    
    @property
    def distinct_word_count(self):
        """Return the number of distinct words in the text."""
        if self._src_type in ['text', 'path']:
            return len(set(self._words(casesensitive=False)))
    
    @property
    def words(self):
        """Return all words in the text as a list."""
        if self._src_type == 'text':
            self._content = self._orig_content
            return self._words(casesensitive=False)
    
        if self._src_type == 'path':
            self._content = self._read_from_file(self.src)
            return len(set(self._words(casesensitive=False)))
    
    @property
    def positivity(self):
        """Return a positivity score of the text."""
        tally = 0
        with open('fca/positive.txt', 'r', encoding='utf-8') as pos_file, \
             open('fca/negative.txt', 'r', encoding='utf-8') as neg_file:   # See NOTE at the beginning of the script.
        
            positive_words = set(pos_file.read().lower().split())
            negative_words = set(neg_file.read().lower().split())

            words = self._words(casesensitive=False)
            words = [word.strip(string.punctuation).lower() for word in self._words()]

            tally = sum(1 if word in positive_words else -1 if word in negative_words else 0 for word in words)
            word_count = self.word_count
            return tally / word_count * 1000 if word_count > 0 else 0
    
if __name__ == "__main__":
    print("Now testing the Analyzer class..."'\n')

#########################

# Content Sources.
url = ('https://en.wikisource.org/wiki/Barack_Obama%27s_First_Inaugural_Address') 
url2 = ('https://en.wikisource.org/wiki/George_W._Bush%27s_Second_Inaugural_Address')
path = ('fca/a-room-with-a-view.txt')    # See NOTE at the beginning of the script.
text = '''A straggling few got up to go in deep despair. The rest
Clung to that hope which springs eternal in the human breast;
They thought, "If only Casey could but get a whack at that--
We'd put up even money now, with Casey at the bat."

But Flynn preceded Casey, as did also Jimmy Blake,
And the former was a hoodoo, while the latter was a cake;
So upon that stricken multitude grim melancholy sat,
For there seemed but little chance of Casey getting to the bat.'''  # Excerpt of text from Poem "Casey at the Bat" by Ernest Lawrence Thayer. https://www.poetry.com/poem/12844/casey-at-the-bat

# Initialize Analyzer with the source and type.
analyze = Analyzer(src=text, src_type='text')
analyze_url = Analyzer(src=url, src_type='url')
analyze_url2 = Analyzer(src=url2, src_type='url')
analyze_room_view = Analyzer(src=path, src_type='path')

#########################  

# Documentation for the Analyzer class.
help(Analyzer)
"""Use help() to view the documentation of the Analyzer class and its methods."""

#########################

# Plot the most common words.
analyze.plot_common_words()

# Plot the character distribution.
analyze.plot_char_distribution()
 
# Extract and print the most common words.
common_words = analyze.common_words()
print("The most common words found in the text are: ")
for word, count in common_words:
    print(f"{word}: {count}")

# Print the average word length.
print('\n'f"The average word length is: {analyze.avg_word_length}"'\n')

#########################

# Data analysis of the content.

# Scraping the word count in Barak Obama's First Inaugural Address.
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
content = soup.find('div', id='bodyContent')

if content:
    obama_words = content.text.lower().split()
    word_count = len(obama_words)
    print(f"The number of words in Barak Obama's First Inaugural Address is: {word_count}")
else:
    print("Unable to find any content to analyze.")

# Scraping the word count in George W. Bush's Second Inaugural Address.
response = requests.get(url2)
soup = BeautifulSoup(response.text, 'html.parser')
content = soup.find('div', id='bodyContent')

if content:
    bushes_words = content.text.lower().split()
    word_count = len(bushes_words)
    print(f"The number of words in George W. Bush's Second Inaugural Address is: {word_count}"'\n')
else:
    print("Unable to find any content to analyze.")

# Least common letter in the "a room with a view" text.
char_distribution = analyze_room_view.char_distribution()
if char_distribution:
    least_common_letter = char_distribution[-1][0]
    print(f"The least common letter in a room with a view is: {least_common_letter}")
else:
    print("Unable to find any content to analyze.")

# Most common 7-letter word in the "a room with a view" text.
common_7_letter = analyze_room_view.common_words(minlen=7, maxlen=7, count=1)
if common_7_letter:
    most_common_word = common_7_letter[0][0]
    print(f"The most common 7-letter word found in the text is: {most_common_word}")
else:
    print("Unable to find any content to analyze.")

# The average word length in the "a room with a view" text.
word_length = analyze_room_view.avg_word_length
print(f"The average word length in the text is: {word_length}")

# How many words, ignoring case, are used only once in the text?
word_count = analyze_room_view._words(casesensitive=False)
word_counts = Counter(word_count)
words_used_once = [word for word, count in word_counts.items() if count ==1]
num_words_used_once = len(words_used_once)
print(f"The number of words used only one time in the text is: {num_words_used_once}")

# How many distinct words in the a room with a view text have fewer than five characters, at least one character of which is a capital A? 
# See NOTE at the beginning of the script.
with open('fca/a-room-with-a-view.txt', 'r', encoding='utf-8') as file:
    text = file.read()
text = re.sub(r'[^\w\s]', ' ', text)
words = re.findall(r'\b\w+\b', text)
filtered_words = {word for word in words if len(word) < 5 and 'A' in word}
num_distinct_words = len(filtered_words)
print(f"The number of distinct words with fewer than five characters and at least one capital A is: {num_distinct_words}")

# How many distinct palindromes of at least three letters are there in a room with a view text.
# See NOTE at the beginning of the script.
with open('fca/a-room-with-a-view.txt', 'r', encoding='utf-8') as file:
    text = file.read()
words = re.findall(r'\b\w+\b', text)
palindromes = [word for word in words if word == word[::-1] and len(word) >= 3]
num_palindromes = len(set(palindromes))
print(f"The number of distinct palindromes of at least three letters in the text is: {num_palindromes}")

# What is the positivity rating of the a room with a view text?
rating = analyze_room_view.positivity
print(f"The positivity rating of the a room with a view text is: {rating}")

# How many distinct words are there in a room with a view text?
distinct_word_count = analyze_room_view.distinct_word_count
print(f"The number of distinct words in the a room with a view text is: {distinct_word_count}"'\n')

# Which of the following two Inaugural addresse has the lowest positivity score?
rating = analyze_url.positivity
rating2 = analyze_url2.positivity
if rating < rating2:
    print("Barak Obama's First Inaugural Address has a lower positivity score.")
elif rating > rating2:
    print("George W. Bush's Second Inaugural Address has a lower positivity score.")
print(f"The positivity score of Barak Obama's First Inaugural Address is: {rating}")
print(f"The positivity score of George W. Bush's Second Inaugural Address is: {rating2}")