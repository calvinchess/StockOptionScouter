import requests

def get_html(url):
    response = requests.get(url)

    return response.text

def parseElement(html, elementIndex):
    stack = []
    lastIndex = -1
    for i in range(elementIndex, len(html)):
        if html[i] == '<':
            if html[i + 1] == "/":
                i = i + 2
                key = ""
                while html[i] != ">":
                    key = key + html[i]
                    i = i + 1
                
                lastIndex = i
                
                while len(stack) > 0 and stack[len(stack) - 1] != key:
                    stack.pop(len(stack) - 1)
                
                if len(stack) > 0:
                    stack.pop(len(stack) - 1)
                
                if len(stack) == 0:
                    break

            else:
                initialIndex = i
                while html[i] != ' ' and html[i] != '>':
                    i = i + 1
                
                element = html[(initialIndex + 1):i]
                stack.append(element)
    
    return html[elementIndex:(lastIndex + 1)]

# returns a list of all the portions that include that class
def find_classes(html, key):
    elements = []
    lastBracket = -1
    for i in range(0, len(html) - len("class")):
        if html[i] == '<':
            lastBracket = i
        
        if html[i:(i + len("class"))] == "class":
            quotationCount = 0
            currentIndex = i + 6
            while quotationCount < 2:
                if html[currentIndex] == '\"':
                    quotationCount = quotationCount + 1
                currentIndex = currentIndex + 1
            
            classes_substring = html[(i + 7):(currentIndex - 1)]

            classes = classes_substring.split()
            for c in classes:
                if c == key:
                    elements.append(parseElement(html, lastBracket))
                    break
    return elements


url = "https://www.marketwatch.com/investing/stock/aapl/options"
pure_html = get_html(url)

all_classes = find_classes(pure_html, "option__heading")

good_classes = []
for i in range(len(all_classes)):
    if "Expires" in all_classes[i]:
        good_classes.append(all_classes[i])
    print(all_classes[i])

# print(all_classes[0][0:1000])
