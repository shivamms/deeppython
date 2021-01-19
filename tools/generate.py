from jinja2 import Template
import os
import json
import shutil
import sys
import argparse


def get_paths():
    paths_dic = {}
    paths_dic["exec_path"] = os.path.abspath(os.path.dirname(sys.argv[0]))
    paths_dic["site_path"] = os.path.abspath(os.path.join(paths_dic["exec_path"], os.pardir))
    parser = argparse.ArgumentParser(description='Get website path')
    parser.add_argument('--sitepath', default=paths_dic["site_path"])
    args = parser.parse_args()
    paths_dic["site_path"] = args.sitepath
    paths_dic["site_config_path"] = os.path.join(paths_dic["site_path"],"config")
    paths_dic["site_config_file"] = os.path.join(paths_dic["site_config_path"],"site.json")
    with open(paths_dic["site_config_file"]) as f:
        site_config = json.load(f)
    f.close()
    paths_dic["template_folder"] = os.path.join(paths_dic["site_path"],"templates",site_config["template"])
    paths_dic["blog_config_path"] = os.path.join(paths_dic["site_config_path"],site_config["template"])
    paths_dic["post_config_path"] = os.path.join(paths_dic["blog_config_path"],"posts")
    paths_dic["post_path"] = os.path.join(paths_dic["site_path"],"posts")
    return paths_dic, site_config


def get_blog(blog_config_path):
    blog_config_file = os.path.join(blog_config_path, "blog.json")
    with open(blog_config_file) as f:
        blog_config = json.load(f)
    return blog_config


def set_post_folder(site_path,posts_names,template_folder):
    posts_meta_dic = {}
    posts_path = os.path.join(site_path,"posts")
    if os.path.isdir(posts_path):
        shutil.rmtree(posts_path)
    os.mkdir(posts_path)
    for post in posts_names:
        post_sys_name = post["name"].replace(" ","")
        post_file_name = post["name"].replace(" ","-")
        post["post_sys_name"] = post_sys_name
        post["post_file_name"] = post_file_name
        post_dir = os.path.join(posts_path, post["post_sys_name"])
        post["post_dir"] = post_dir
        if not os.path.isdir(post["post_dir"]):
            shutil.copytree(template_folder,post["post_dir"])
        post["post_html"] = os.path.join(post["post_dir"],"html","Blog-" + post["post_file_name"] + ".html")
        post["post_html_relative"] = post["post_html"].replace(site_path,"../../..")
        post_index_html = os.path.join(post["post_dir"],"html","index.html")
        if not os.path.isfile(post["post_html"]) and os.path.isfile(post_index_html):
            shutil.move(post_index_html,post["post_html"])
        elif not os.path.isfile(post_index_html) and not os.path.isfile(post["post_html"]):
            shutil.copy(os.path.join(template_folder,"html","index.html"), post["post_html"])
        posts_meta_dic[post["name"]] = post
    return posts_meta_dic


def get_posts(post_config_path,posts_meta_dic,site_path):
    posts_dic = {}
    post_meta_list = []
    for key,value in posts_meta_dic.items():
        post_meta = value
        post_config_file = os.path.join(post_config_path, post_meta["post_sys_name"] + ".json")
        with open(post_config_file) as f:
            posts_dic[post_meta["name"]] = (json.load(f))
        f.close()
        content_folder = os.path.abspath(posts_dic[post_meta["name"]]["contentFolder"])
        content_file = os.path.join(content_folder,post_meta["post_sys_name"]+".html")
        posts_dic[post_meta["name"]]["contentFile"] = content_file
        posts_dic[post_meta["name"]]["contentFile_relative"] = content_file.replace(site_path,"../../..")
        post_meta_list.append(post_meta)
    return posts_dic, post_meta_list


def set_post_files(blog_dic,posts_meta_dic,posts_dic,navigation_dic,post_meta_list):
    for key,value in posts_meta_dic.items():
        post_meta = value
        post_html = post_meta["post_html"]
        with open(post_html, 'r') as f:
            content = f.read()
        tm = Template(content)
        content = tm.render(post=posts_dic[post_meta["name"]], posts=post_meta_list, blog=blog_dic, navigation=navigation_dic)
        f.close()
        f = open(post_html, "w", encoding="utf-8")
        f.write(content)
        f.close()

def set_default(default_post_meta_dic,site_path):
    default_dic = {}
    default_dic["post_url"] = default_post_meta_dic["post_html"]
    default_dic["post_url_index_file"] = default_post_meta_dic["post_html"].replace(site_path+"/","")
    default_dic["post_url_relative"] = default_post_meta_dic["post_html"].replace(site_path, "../../..")
    return default_dic


def set_default_page(site_path,default_post_meta_dic,default_dic):
    index_file = os.path.join(site_path,"index.html")
    index_file_template = os.path.join(site_path, "index.html.template")
    if os.path.isfile(index_file):
        os.remove(index_file)
    shutil.copy(index_file_template,index_file)
    with open(index_file, 'r') as f:
        content = f.read()
    tm = Template(content)
    content = tm.render(default=default_dic)
    f.close()
    f = open(index_file, "w", encoding="utf-8")
    f.write(content)
    f.close()


paths, site = get_paths()
blog = get_blog(paths["blog_config_path"])
posts_name_list = blog["posts"]
navigation = blog["navigation"]
posts_meta = set_post_folder(paths["site_path"],posts_name_list,paths["template_folder"])
default = set_default(posts_meta[blog["default_post"]],paths["site_path"])
posts, post_meta_list = get_posts(paths["post_config_path"],posts_meta,paths["site_path"])
for item in navigation:
    item["href"] = default["post_url_relative"]
set_post_files(blog,posts_meta,posts,navigation,post_meta_list)
set_default_page(paths["site_path"],posts_meta[blog["default_post"]],default)

