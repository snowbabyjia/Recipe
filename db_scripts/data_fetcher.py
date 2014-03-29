import urllib2
import nltk

url_first = 'http://allrecipes.com/Recipe/Easy-Lasagna-II/'
recipes = []
seen = []

def get_url( name):
    return 'http://allrecipes.com/Recipe/' + name



def find_inf(TEMPLATE, html):
    index = 0
    s = html.find(TEMPLATE, index)
    data = []
    while s != -1 :
        key = ""
        s += len(TEMPLATE)
        i = 0
        while html[s+i] != '<' and html[s+i] != '"' and html[s+i] != '/':
            key += html[s+i]
            i+=1
        data.append(key)
        index = s+1
        s = html.find(TEMPLATE, index)
    return data

def add_recipes(url):
    print url
    if len(recipes)<100 and not url in seen:
        seen.append(url)
        response = urllib2.urlopen(url)
        html = response.read()
        add = True
        data = {}
        data['recipe_name'] = find_inf('<h1 id="itemTitle" class="plaincharacterwrap fn" itemprop="name">', html)[0]
        ings = find_inf('<span id="lblIngName" class="ingredient-name">', html)
        data['ingredients'] = []
        #print  ings
        for i in range(len(ings)):
            #print "raw Ing : " + str( ings[i])
            words = nltk.word_tokenize(ings[i])
            tags = nltk.pos_tag(words)
            #print tags
            final = []
            for l in range(len(tags)):
                if tags[l][1][0:2] == 'NN' or tags[l][1][0:2] == 'IN':
                    final.append(tags[l][0])
            if len(final)>0:
                ing= final[0]
                for i in range(1, len(final)):
                    ing+= " " + final[i]
                print "Final Ing: " + str(ing)
                data['ingredients'].append( ing )
        
        rat = find_inf('<meta itemprop="ratingValue" content="', html)
        if len(rat) ==0:
            add = False
        else:
            data['rating'] = find_inf('<meta itemprop="ratingValue" content="', html)[0]
        data['url'] = url

        if add:
            recipes.append(data)

        next = find_inf('<a href="/Recipe/', html)
        for i in next:
            add_recipes(get_url(i))


if __name__ == "__main__":
    add_recipes(url_first)
    print recipes
    print len(recipes)

    not_inc = ["salt", "pepper", "oil", "water"]
    not_req = ["garlic", "spices"]
    
    output_file = open("recipes.txt", "w")
    
    for i in recipes:
        for j in i['ingredients']:
            if not j in not_inc:
                if j in not_req:
                    output_file.write(" "+ i['recipe_name'] + "| "+ j + " | 1 | False | "+ str(i['rating'])+" | " + i['url'] + "\n")
                else:
                     output_file.write(" "+ i['recipe_name'] + "| "+ j + " | 1 | True | "+str(i['rating'])+" | " + i['url'] + "\n")

    output_file.close()
    
            

