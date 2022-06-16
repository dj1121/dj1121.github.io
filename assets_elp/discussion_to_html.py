"""
A script to convert (n) canvas discussion post pages (w/ images) into a neat PDF
Required: Full canvas discussion webpages saved from Google Chrome
Author: Devin Johnson
Last Updated: June, 2022
Files MUST be named as such and kept in directory as such (assuming n=2 pages of discussion posts):
                                        -canvas_pages\n\
                                        \t--canvas_1_files\n\
                                        \t--canvas_1.html\n\
                                        \t--canvas_2\n\
                                        \t--canvas_2.html\n\
                                        \t--....", default =__file__)
"""

###################### Imports ######################
#####################################################

from ctypes.wintypes import HMODULE
from fileinput import filename
import os
import sys
import argparse
import markdown
from bs4 import BeautifulSoup


###################### Constants ######################
#######################################################
INPUT_DIR = ""

###################### Classes ######################
#######################################################
class UserPost:
    def __init__(self, name="", text="", images=None):
        self.name = name
        self.text = text
        self.images = images

    def __str__(self):
        string = "--" + self.name + "--" + "\n" + self.text + "\n"
        if self.images != None:
            for image in self.images:
                string += (" " + str(image)) 
        return string

    def get_side_html(self):
        return "<li><a href=\"#" + self.name +"\" class=\"active\"> "  + self.name + "</a></li>"

    def get_post_html(self):

        # Wraps the post
        string = "<article class=\"people-small\">\n" + "<div class=\"people-wrap\">"
        
        if self.images != None and self.images != []:
            for i, image in enumerate(self.images):
                image = image.replace(".", "canvas_pages", 1)
                string += "\t<div class=\"people-image\"\n>" + "\t<img src=\"" + image + "\" alt=\"" + self.name.split()[0] + "\" />\n" + "</div>\n"
        else: 
            string += "<div class=\"people-image\"\n>" + "\t<img src=\"canvas_pages/2.jpg\" alt=\"\" />\n" + "</div>\n"


        string += "<div class=\"people-content\">\n" + "\t<h2>" + "<a id=\"" + self.name + "\">" + self.name + "</a></h2>\n</div></div>"
        string += "<p>" + self.text + "</p></article>\n\n"
        

        return string


###################### Functions ######################
#######################################################

# Parse input arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-in_dir",type=str, help = "Path to directory containing full webpages.\
                                                    Directory should look like (if 2 pages of discussion included):\
                                                                    -canvas_pages\n\
                                                                    \t--canvas_1_files\n\
                                                                    \t--canvas_1.html\n\
                                                                    \t--canvas_2\n\
                                                                    \t--canvas_2.html\n\
                                                                    \t--....", default = "./canvas_pages/")
    args = parser.parse_args()
    return args

# Returns posts on an html page as a list of UserPost objects
def parse_html(html_file):

    author_post = True   
    page_posts = []

    f = open(html_file, "r", encoding="utf-8")
    soup = BeautifulSoup(f, 'html.parser')
    
    # Get all user post text and images
    post = UserPost()
    spans = soup.find_all('span', {'class' : 'user_content enhanced'})
    for span in spans:
        parents = span.findParents()
        for parent in parents:
            if parent.get('data-testid') != None and parent.get('data-testid') == 'author_name':
                post.name = span.text

            if parent.get('class') != None and " ".join(parent.get('class')) == 'fOyUs_bGBk fOyUs_fhgP fOyUs_divt dJCgj_bGBk':
                if span.find_all('img') != "":
                    post.images = []
                    images = span.find_all('img')
                    for image in images:
                        url = image.get('src')
                        post.images.append(url)
                
                post.text = span.text
                
        if post.name != "" and post.text != "":
            if author_post:
                post.text = ""
                author_post = False
            else:
                page_posts.append(post)
                post = UserPost()

    return page_posts

def output(all_posts):

    f = open("index.html", "w", encoding = "utf-8")

    with open("html_templates/html_top.html", "r") as top:
            for line in top.readlines():
                f.write(line)
    
    for post in all_posts:
        f.write(post.get_side_html() + "\n")
    
    with open("html_templates/html_middle.html", "r") as middle:
            for line in middle.readlines():
                f.write(line)

    for post in all_posts:
        f.write(post.get_post_html())
    
    with open("html_templates/html_bottom.html", "r") as bottom:
            for line in bottom.readlines():
                f.write(line)

    f.close()    

###################### Main ###########################
#######################################################

if __name__ == "__main__":

    args = parse_args()
    INPUT_DIR = args.in_dir
    
    # Print relevant accessed files/folders, doesn't print others in path
    html_files = []
    print("ACCESSED FILES/FOLDERS:\n\t#######################################")
    for f in os.listdir(INPUT_DIR):
        print("\t --" + f)
        if "html" in f:
            html_files.append(INPUT_DIR + "/" + f)
    print("\t#######################################")

    # Parse each HTML file + accompanying folder
    all_posts = []
    for i in range(len(html_files)):
        page_posts = parse_html(html_files[i])
        for post in page_posts:
            all_posts.append(post)

    
    # Order the posts by name and output to html
    all_posts.sort(key=lambda x: x.name.split()[-1])
    print("\nOUTPUTTING " + str(len(all_posts)) + " POSTS TO HTML.")
    output(all_posts)


