import pandas as pd
import streamlit as st
import os
from PIL import Image
from pathlib import Path
import json
import numpy as np
from streamlit_drawable_canvas import st_canvas


def page_configs():
    ### Set page config
    st.set_page_config(layout="wide",)
    pd.set_option('future.no_silent_downcasting', True)


def init_state():
    ### Initialize
    if "annotate_json_data" not in st.session_state:
        st.session_state["annotate_json_data"] = {}

    if "sidebar_option" not in st.session_state:
        _sidebar_option = {
            "drawing_tools": ("rect", "transform"),
            "json_options" : ("canvas", "labelme")
        }
        st.session_state["sidebar_option"] = _sidebar_option

    if "curr_image_info" not in st.session_state:
        st.session_state["curr_image_info"] = {}
        st.session_state["curr_image_info"]["image_name"] = None
        st.session_state["curr_image_info"]["image"] = None
        st.session_state["curr_image_info"]["image_width"] = None
        st.session_state["curr_image_info"]["image_height"] = None
        st.session_state["curr_image_info"]["json_file_name"] = None
        st.session_state["curr_image_info"]["json_data"] = None

    if "canvas_template" not in st.session_state:
        template = {
            "type": "rect",
            "version": "4.4.0",
            "originX": "left",
            "originY": "top",
            "left": None,
            "top": None,
            "width": None,
            "height": None,
            "fill": "rgba(0, 0, 0, 0.3)",
            "stroke": None,
            "strokeWidth": 2,
            "strokeDashArray": None,
            "strokeLineCap": "butt",
            "strokeDashOffset": 0,
            "strokeLineJoin": "miter",
            "strokeUniform": True,
            "strokeMiterLimit": 4,
            "scaleX": 1,
            "scaleY": 1,
            "angle": 0,
            "flipX": False,
            "flipY": False,
            "opacity": 1,
            "shadow": None,
            "visible": True,
            "backgroundColor": "",
            "fillRule": "nonzero",
            "paintFirst": "fill",
            "globalCompositeOperation": "source-over",
            "skewX": 0,
            "skewY": 0,
            "rx": 0,
            "ry": 0,
            "Class": None
        }
        st.session_state["canvas_template"] = template

    if "color_df" not in st.session_state:
        # Color List
        color_list = [
            {'Color': 'Red', 'Class': None},
            {'Color': 'Green', 'Class': None},
            {'Color': 'Blue', 'Class': None},
            {'Color': 'Yellow', 'Class': None},
            {'Color': 'Cyan', 'Class': None},
            {'Color': 'Magenta', 'Class': None},
            {'Color': 'Orange', 'Class': None},
            {'Color': 'Purple', 'Class': None},
            {'Color': 'Pink', 'Class': None},
            {'Color': 'Brown', 'Class': None},
            {'Color': 'Gray', 'Class': None},
            {'Color': 'Black', 'Class': None},
            {'Color': 'White', 'Class': None},
            {'Color': 'Beige', 'Class': None},
            {'Color': 'Teal', 'Class': None},
            {'Color': 'Navy', 'Class': None},
            {'Color': 'Maroon', 'Class': None},
            {'Color': 'Olive', 'Class': None},
            {'Color': 'Lime', 'Class': None},
            {'Color': 'Coral', 'Class': None},
            {'Color': 'Gold', 'Class': None},
            {'Color': 'Silver', 'Class': None}
        ]
        st.session_state["color_df"] = pd.DataFrame(color_list)

    if "drawing_mode" not in st.session_state:
        st.session_state["drawing_mode"] = None

    if "stroke_width" not in st.session_state:
        st.session_state["stroke_width"] = None

    if "retain" not in st.session_state:
        st.session_state["retain"] = None

    if "displayed_color_df" not in st.session_state:
        st.session_state["displayed_color_df"] = None

    if "canvas_result" not in st.session_state:
        st.session_state["canvas_result"] = None

    if "default_value" not in st.session_state:
        st.session_state["default_value"] = 0


def _load_image(image_path):
    ### Read image
    image = Image.open(image_path)
    width, height = image.size

    return image, width, height


def _load_json_data(data_dir, image_name):
    ### Read json data
    json_file_name = image_name.replace(Path(image_name).suffix, ".json")
    json_file_path = os.path.join(data_dir, json_file_name)

    if os.path.exists(json_file_path):
        json_data = json.load(open(json_file_path, "r"))
    else:
        json_data = {}
    
    return json_file_name, json_data


def load_data_with_tools():
    ### Load image list
    image_types = (".jpg", ".png", ".jpeg")

    ### Image directory
    data_dir = st.text_input("Enter image directory:",
                             "C:\\data_annotator")
    
    ### Search image
    search_image = st.text_input("Search image:")
    
    ### Extract image
    image_list = list(filter(lambda x: x.endswith(image_types),
                             os.listdir(data_dir)))
    
    ### Display slider for switching image
    if len(image_list) > 1:
        curr_image_index = st.slider("Select image", 0, len(image_list)-1)
    else:
        curr_image_index = st.slider("Select image", 0, disabled=True)

    ### Read image
    if search_image:

        if search_image in image_list:
            index = image_list.index(search_image)
            image_name = image_list[index]
        
        else:
            st.error("No such image")
            st.stop()

    else:
        image_name = image_list[curr_image_index]
    
    image_path = os.path.join(data_dir, image_name)
    image, width, height = _load_image(image_path)

    ### Read json
    json_file_name, json_data = _load_json_data(data_dir, image_name)

    ### Update session_state
    st.session_state["curr_image_info"]["image_name"] = image_name
    st.session_state["curr_image_info"]["image"] = image
    st.session_state["curr_image_info"]["image_width"] = width
    st.session_state["curr_image_info"]["image_height"] = height
    st.session_state["curr_image_info"]["json_file_name"] = json_file_name
    st.session_state["curr_image_info"]["json_data"] = json_data


def _labelme_to_canvas(coords_info_list):
    ### Create canvas format template
    root = {
            "version": "4.4.0",
            "objects": []
    }

    canvas_template = st.session_state["canvas_template"]

    ### Convert each annotation's label, coords, color to canvas format and store into session state
    for coords_info in coords_info_list:
        template = canvas_template.copy()

        label, x1, y1, x2, y2, color = coords_info

        template["left"] = x1
        template["top"] = y1
        template["width"] = x2 - x1
        template["height"] = y2 - y1
        template["stroke"] = color
        template["Class"] = label

        root["objects"].append(template)

    return root


def transform_data():
    ### Load current image json data
    json_data = st.session_state["curr_image_info"]["json_data"]
    
    ### Initialize color df for each image if "Retain color list" is False
    if not st.session_state["retain"]:
        st.session_state["color_df"]["Class"] = None
    color_df = st.session_state["color_df"]

    ### For labelme json
    if json_data.get("shapes", 0):

        coords_info_list = []

        for coords_info in json_data["shapes"]:
            label = coords_info["label"]
            xyxy = coords_info["points"]
            x1, y1, x2, y2 = xyxy[0][0], xyxy[0][1], xyxy[1][0], xyxy[1][1]

            ### Check if the label (class name) exist in color df
            if any(color_df["Class"]==label):
                color = color_df[color_df["Class"]==label]["Color"].values[0]
            else:
                ### If the label (class name) not exist in color df
                ### Extract the first empty class's color and Store the label (class name) into color df
                color = color_df[color_df["Class"].isna()]["Color"].head(1).values[0]
                st.session_state["color_df"].loc[st.session_state["color_df"]["Color"]==color, "Class"] = label

            ### Store all bounding box with color into coords_info_list
            coords_info_list.append([label, x1, y1, x2, y2, color])

        ### Store into session state
        st.session_state["curr_image_info"]["json_data"] = _labelme_to_canvas(coords_info_list)

    ### For canvas json
    elif json_data.get("objects", 0):

        for coords_info in json_data["objects"]:

            color = coords_info["stroke"]

            if coords_info.get("Class", 0):
                ### Add class name to color df
                label = coords_info["Class"]
                st.session_state["color_df"].loc[st.session_state["color_df"]["Color"]==color, "Class"] = label

            else:
                ### Create a default class name for each bounding box
                if st.session_state["color_df"].loc[st.session_state["color_df"]["Color"]==color, "Class"].values[0] is None:
                    ### Update class name for the color
                    default_value = f"obj-{st.session_state['default_value']}"
                    st.session_state["color_df"].loc[st.session_state["color_df"]["Color"]==color, "Class"] = default_value
                    st.session_state['default_value'] += 1

        st.session_state["curr_image_info"]["json_data"] = json_data


def sidebar_features():
    ### Drawing tools
    drawing_mode = st.sidebar.selectbox("Drawing tools", st.session_state["sidebar_option"]["drawing_tools"])

    ### Stroke width
    stroke_width = st.sidebar.slider("Stroke width: ", 1, 15, 2)

    ### Retain color list
    retain = st.sidebar.checkbox("Retain color list")

    ### Object Class
    class_list = st.sidebar.data_editor(st.session_state["color_df"],
                                        disabled=["Color"],
                                        use_container_width=True,
                                        key="class_df")
    
    st.session_state["drawing_mode"] = drawing_mode
    st.session_state["stroke_width"] = stroke_width
    st.session_state["retain"] = retain
    st.session_state["displayed_color_df"] = class_list

def _add_class_name(json_data):
    for coords_info in json_data["objects"]:

        ### Extract color and class name for each bounding box
        color = coords_info["stroke"]
        label = st.session_state["displayed_color_df"].loc[st.session_state["displayed_color_df"]["Color"]==color, "Class"].values[0]

        ### Add new key: "Class"
        coords_info["Class"] = label

def _export_json_file(json_file_name, json_data):
    ### Write json file
    with open(json_file_name, "w") as json_file:
        json_object = json.dumps(json_data, indent=4)
        json_file.write(json_object)

def _export_labelme_json_file(img_name, json_file_name, json_data, img_width, img_height):
    template = {
                "version": "4.4.0",
                "flags": {},
                "shapes": [],
                "imagePath": None,
                "imageData": None,
                "imageHeight": None,
                "imageWidth": None
            }
    
    coords_info = {
                    "label": None,
                    "points": None,
                    "group_id": None,
                    "shape_type": "rectangle",
                    "flags": {}
                }
    
    for data in json_data["objects"]:
        x1, y1, w, h = data["left"], data["top"], data["width"], data["height"]
        x2, y2 = x1 + w, y1 + h

        data_template = coords_info.copy()

        data_template["points"] = [[x1, y1], [x2, y2]]
        data_template["label"] = data["Class"]

        template["shapes"].append(data_template)

    template["imageHeight"] = img_height
    template["imageWidth"] = img_width
    template["imagePath"] = img_name

    _export_json_file(json_file_name, template)


def canvas_drawing():
    ### Extract current class as selectbox options
    displayed_color_df = st.session_state["displayed_color_df"]
    defined_class = displayed_color_df[displayed_color_df["Class"].notnull()]["Class"]
    curr_class = st.selectbox("Define class to annotate", defined_class)

    if any(displayed_color_df["Class"].notnull().values):
        color = displayed_color_df[displayed_color_df["Class"] == curr_class]["Color"].values[0]
    else:
        color = None

    image_name = st.session_state["curr_image_info"]["image_name"]
    width = st.session_state["curr_image_info"]["image_width"]
    height = st.session_state["curr_image_info"]["image_height"]
    json_file_name = st.session_state["curr_image_info"]["json_file_name"]

    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=st.session_state["stroke_width"],
        stroke_color=color,
        background_image=st.session_state["curr_image_info"]["image"],
        update_streamlit=True,
        width=width,
        height=height,
        drawing_mode=st.session_state["drawing_mode"],
        initial_drawing=st.session_state["curr_image_info"]["json_data"],
        key=image_name,
    )

    if canvas_result.json_data is not None and canvas_result.json_data["objects"] != []:

        _add_class_name(canvas_result.json_data)

        ### Display bounding box information
        display_df = pd.DataFrame(canvas_result.json_data["objects"])
        display_df = display_df[["type", "version", "left", "top", "width", "height", "fill", "stroke", "strokeWidth", "Class"]]
        st.dataframe(display_df)

        st.session_state["canvas_result"] = canvas_result.json_data

        if st.button("Export canvas.json"):
            _export_json_file(json_file_name, canvas_result.json_data)
            st.success(f'{json_file_name} exported!', icon="✅")

        if st.button("Export labelme.json"):
            _export_labelme_json_file(image_name, json_file_name, canvas_result.json_data, width, height)
            st.success(f'{json_file_name} exported!', icon="✅")