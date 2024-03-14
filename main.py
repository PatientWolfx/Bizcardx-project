import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import re
import cv2
import easyocr
import os
import matplotlib.pyplot as plt
import psycopg2
from PIL import Image
from streamlit_lottie import st_lottie
import json
import requests


#Connecting DB

mydb = psycopg2.connect(
    host = 'localhost', 
    user = 'postgres', 
    password = 'Abu#@7899#', 
    port = 5432, 
    database = 'bizcardx'
)

mycursor = mydb.cursor()
mydb.commit()

#Creating table
create_query = '''
CREATE TABLE IF NOT EXISTS card_details(
id SERIAL PRIMARY KEY, 
company_name VARCHAR(255), 
card_holder VARCHAR(255), 
designation VARCHAR(255), 
mobile_number VARCHAR(255), 
email VARCHAR(255), 
website VARCHAR(255), 
area VARCHAR(255), 
city VARCHAR(255), 
state VARCHAR(255), 
pin_code VARCHAR(10), 
image BYTEA
)
'''
mydb.cursor(create_query)
mydb.commit()

img1 = Image.open(r'image\pg_icon.jpg')
st.set_page_config(page_title = 'BizcardX', page_icon = img1, layout = 'wide')
st.title(':black[Extracting Business Card Data with OCR]')

#Removing the menu button
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

#Creating option menu
selected = option_menu(
    menu_title = None, 
    options = ['Home', 'Upload and preview image', 'Manipulate data'],
    icons = ['house', 'image', 'database'],
    menu_icon = 'cast', 
    default_index = 0,
    orientation = 'horizontal',
    styles = {
        'container': {'padding':'10px', 'background-color':'#29ADB2'}, 
        'icon': {'color': '#F3F3F3', 'font-size': '25px'}, 
        'nav-link': {
            'font-size': '25px', 
            'text-align': 'center', 
            'margin': '0px', 
            '--hover-color': '#C5E898'
        }, 
        'nav-link-selected': {'background-color':'#C5E898'}
    }
)

#Home
if selected == 'Home':
    c1, c2 = st.columns([3, 2])
    with c1:
        st.header('BizcardX')
        st.write('''
        This Streamlit web application provides users with the capability 
        to extract essential details from uploaded images using EasyOCR. 
        The extracted information can be seamlessly uploaded into a database,
        where users can subsequently view, modify, and delete the stored data. 
        The application focuses on facilitating efficient extraction and management 
        of key data elements from images through a straightforward and user-friendly interface.
        '''
        )
        st.markdown('''## Technologies used: 
        OCR, streamlit, SQL, Data Extraction''')
        
    with c2:
        def load_lottiefile(filepath: str):
            with open(filepath, 'r') as f:
                return json.load(f)

        def load_lottieurl(url: str):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()

        lottie_hello = load_lottieurl('https://lottie.host/40a85fea-853a-406d-b7f2-64f0920d0816/YqoivM5TDM.json')
        lottie_coding = load_lottiefile('lottiefiles\\Animation - 1701176135952.json')

        st.lottie(
            lottie_coding, 
        # change the direction of our animation 
                  reverse=True, 
                  # height and width of animation 
                  height=400,   
                  width=400, 
                  # speed of animation 
                  speed=1,   
                  # means the animation will run forever like a gif, and not as a still image 
                  loop=True,   
                  # quality of elements used in the animation, other values are "low" and "medium" 
                  quality='high', 
                   # THis is just to uniquely identify the animation 
                  key='code'
        )

#Upload 
if selected == 'Upload and preview image':
    tab1, tab2 = st.tabs(['Undefined text', 'Predefined text'])
    reader = easyocr.Reader(['en'])
    
    with tab1:
        uploaded_card = st.file_uploader('upload image',key='tab1_key', label_visibility='collapsed', type=['png', 'jpeg', 'jpg'])
        
        if uploaded_card is not None:
            button = st.button('Gather data')
            if button:
                def save_card(uploaded_card):
                    with open(os.path.join(r'C:\Users\Enigma\Streamlit\Projects\BizCardX\uploaded cards', 
                                           uploaded_card.name), 'wb') as f:
                        f.write(uploaded_card.getbuffer())

                save_card(uploaded_card)

                def bounding_boxes(image, detection):
                    for bbox, text, prob in detection:
                        cv2.rectangle(image, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 5)
                        cv2.putText(image, text, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 0), 2)

                    plt.rcParams['figure.figsize'] = (4, 4)
                    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGBA))
                    plt.axis('off')
                    plt.show()

                col1, col2 = st.columns([5, 5])
                with col1:
                    with st.spinner('Mapping text on image...'):
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        image_path = r'C:\Users\Enigma\Streamlit\Projects\BizCardX\uploaded cards\\' + uploaded_card.name
                        image = cv2.imread(image_path)
                        result = reader.readtext(image_path)
                        st.pyplot(bounding_boxes(image, result), use_container_width = False)


                #undefined data extraction
                image_path = r'C:\Users\Enigma\Streamlit\Projects\BizCardX\uploaded cards\\' + uploaded_card.name
                detection = reader.readtext(image_path, detail=0, paragraph=True)
                with col2: 
                    data = ''
                    for i in detection:
                        data += i
                    st.write(data)
    
    #predefined text
    with tab2:
        uploaded_card = st.file_uploader('upload image', key='tab2_key', label_visibility='collapsed', type=['png', 'jpeg', 'jpg'])
        
        if uploaded_card is not None:
            button = st.button('Gather and upload data')
            if button:
                def save_card(uploaded_card):
                    with open(os.path.join(r'C:\Users\Enigma\Streamlit\Projects\BizCardX\uploaded cards', 
                                           uploaded_card.name), 'wb') as f:
                        f.write(uploaded_card.getbuffer())

                save_card(uploaded_card)

                def bounding_boxes(image, detection):
                    for bbox, text, prob in detection:
                        cv2.rectangle(image, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 5)
                        cv2.putText(image, text, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 0), 2)

                    plt.rcParams['figure.figsize'] = (4, 4)
                    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGBA))
                    plt.axis('off')
                    plt.show()                

                col1, col2 = st.columns(2, gap = 'large')
                #with col1:
                with st.spinner('Mapping text on image...'):
                    st.set_option('deprecation.showPyplotGlobalUse', False)
                    image_path = r'C:\Users\Enigma\Streamlit\Projects\BizCardX\uploaded cards\\' + uploaded_card.name
                    image = cv2.imread(image_path)
                    result = reader.readtext(image_path)
                    st.pyplot(bounding_boxes(image, result), use_container_width = False)


                #Predefined data extraction
                image_path = r'C:\Users\Enigma\Streamlit\Projects\BizCardX\uploaded cards\\' + uploaded_card.name
                detection = reader.readtext(image_path, detail=0)

                def bi_convert(file):
                    with open(file, 'rb') as f:
                        data = f.read()
                    return data

                data = {"company_name": [],
                        "card_holder": [],
                        "designation": [],
                        "mobile_number":[],
                        "email": [],
                        "website": [],
                        "area": [],
                        "city": [],
                        "state": [],
                        "pin_code": [],
                        'image': bi_convert(image_path)
                        }

                def get_data(detect):
                    for index, i in enumerate(detect):
                        #Company name
                        if index == len(detect)-1:
                            data['company_name'].append(i)
                            if len(data['company_name'][0]) == 8 and i == 'digitals':
                                data['company_name'][0] = detect[-3] + ' ' + detect[-1]

                            elif len(data['company_name'][0])<5:
                                data['company_name'][0] = detect[-4] + ' ' + detect[-2]

                            elif len(data['company_name'][0]) == 8:
                                data['company_name'][0] = detect[-2] + ' ' + detect[-1]

                            elif len(data['company_name'][0]) <= 10:
                                data['company_name'][0] = detect[-3] + ' ' + detect[-1]

                        #Name
                        elif index == 0:
                            data['card_holder'].append(i)

                        #Designation
                        elif index == 1:
                            data['designation'].append(i)

                        #mobile number
                        elif '-' in i:
                            data['mobile_number'].append(i)
                        if len(data["mobile_number"]) == 2:
                             data["mobile_number"] = [" & ".join(data["mobile_number"])]

                        #email
                        elif '@' in i:
                            data['email'].append(i)

                        #Website
                        if 'www ' in i.lower() or 'www.' in i.lower():
                            data['website'].append(i)

                        elif 'WWW' in i:
                            data['website'].append(detect[4] + '.' + detect[5])

                        #Area
                        if re.findall('^[0-9].+, [a-zA-Z]+', i):
                            data['area'].append(i.split(',')[0])

                        elif re.findall('[0-9] [a-zA-Z]+', i):
                            data['area'].append(i+ 'St')

                        #City
                        match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                        match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                        match3 = re.findall('^[E].*', i)
                        if match1:
                            data['city'].append(match1[0])

                        elif match2:
                            data['city'].append(match2[0])

                        elif match3:
                            data['city'].append(match3[0])

                        #State
                        state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                        if state_match:
                            data['state'].append(i[:9])

                        elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                            data['state'].append(i.split()[-1])

                        if len(data['state']) == 2:
                            data['state'].pop(0)

                        #Pincode
                        if re.findall('[a-zA-Z]{9} +[0-9]', i):
                            data['pin_code'].append(i[10:])

                        elif len(i) >= 6 and i.isdigit():
                            data['pin_code'].append(i)

                get_data(detection)
                st.table(data)

                st.success('Data Extracted successfully!')
                
                df = pd.DataFrame(data)

                if button:
                    try:
                        name = data['card_holder'][0]
                        query = f"select * from card_details where card_holder= '{name}'"
                        mycursor.execute(query)
                        result = mycursor.fetchall()
                        z= result[0][2]
                        if name == z:
                            st.warning('Duplicate entry')
                        else:
                            pass
                    except:
                        for i, row in df.iterrows():
                            insert_query = '''
                            INSERT INTO CARD_DETAILS(
                            company_name, 
                            card_holder, 
                            designation, 
                            mobile_number, 
                            email, 
                            website, 
                            area, 
                            city, 
                            state, 
                            pin_code, 
                            image
                            )
                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            '''

                            mycursor.execute(insert_query, tuple(row))
                            mydb.commit()

                        st.success('Successfully uploaded to database!')

                #with col2:
                #st.table(data)
                        
#Data Manipulation

if selected == 'Manipulate data':
    try:
        col1, col2 = st.columns([1, 15])
        with col1:
            select_method = option_menu(
            menu_title = None, 
            options = ['Modify','Delete'],
            icons = ['pencil-square', 'trash'],
            menu_icon = 'cast', 
            default_index = 0,
            orientation = 'horizontal',
            styles = {
                'container': {'padding':'0px', 'background-color':'#29ADB2'}, 
                'icon': {'color': '#F3F3F3', 'font-size': '25px'}, 
                'nav-link': {
                    'font-size': '10px', 
                    'text-align': 'center', 
                    'margin': '0px', 
                    '--hover-color': '#C5E898'
                }, 
                'nav-link-selected': {'background-color':'#C5E898'}
            }
        )
        with col2:
            def get_names():
                names = '''
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'card_details'
                '''
                mycursor.execute(names)
                columns = mycursor.fetchall()
                column_names = [column[0] for column in columns[2:]]
                return column_names
            def create_df():
                        mycursor.execute(f'SELECT {', '.join(column_names)} FROM card_details')
                        result = mycursor.fetchall()
                        df = pd.DataFrame(result, columns = column_names)
                        return df
            if select_method == 'Modify':
                column_names = get_names()
                select = st.selectbox(':green[Select an option to modify]', 
                                      column_names
                                     )
                query = f'SELECT {select} FROM card_details'
                mycursor.execute(query)
                result = mycursor.fetchall()
                business_cards = {}
                for row in result:
                    business_cards[row[0]] = row[0]

                select_values = st.selectbox(f'{select}', list(business_cards.keys()))
                query = f'SELECT {select} FROM card_details WHERE {select} = %s'
                mycursor.execute(query, (select_values,))
                result = mycursor.fetchone()

                modify_select = st.text_input(f'Modify {select}', result[0])

                if st.button('Commit changes'):
                    if select_values != modify_select:
                        query = f'UPDATE card_details SET {select} = %s WHERE {select} = %s'
                        mycursor.execute(query, (modify_select, select_values))
                        mydb.commit()
                        st.success(f'Successfully updated {select} from {select_values} to {modify_select}')
                        st.markdown('####Updated values')
                        df = create_df()
                        st.write(df)
                    else:
                        st.warning('No New entries')
                        df = create_df()
                        st.write(df)

            if select_method == 'Delete':
                column_names = get_names()
                select = st.selectbox(':green[Select an option to delete]', 
                                      column_names
                                     )
                query = f'SELECT {select} FROM card_details'
                mycursor.execute(query)
                result = mycursor.fetchall()
                business_cards = {}
                for row in result:
                    business_cards[row[0]] = row[0]

                select_values = st.selectbox(f'{select}', list(business_cards.keys()))

                if st.button('Delete'):
                    query = f'DELETE FROM card_details WHERE {select} = %s'
                    mycursor.execute(query, (select_values,))
                    mydb.commit()
                    st.success(f'Successfully deleted {select_values} from card_details')
                    df = create_df()
                    st.write(df)
    except:
        st.warning('No data available')