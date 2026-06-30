import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from helper.utils import calculate_distance,is_open_spot
from helper.utils import get_spot_icon

df = pd.read_csv("./dubai_cold_coffee_spots_clean.csv")
df_areas = pd.read_csv("./dubai_areas_label.csv")

st.set_page_config(page_title="Dubai Cold Coffee Finder",
                   page_icon="☕",layout="wide")
st.title("☕ Dubai Cold Coffee Finder")
st.write("Find the nearest cold coffee spots around you in Dubai.")
st.write("Explore cafes, carts, and trucks based on distance, rating, and availability.")

st.header("📍 Select Your Area")

area_labels = list(df_areas["label"])
# area_labels.insert(0,"Select")

selected_area = st.selectbox("Choose your area",area_labels)


with st.sidebar:

   st.header("🔍 Search & Filters")
   spot_name=st.text_input("Search by name",placeholder="eg: Al Safa")

   st.divider()
   st.header("⚙️ Filters")
   options = list(df["type"].unique())
   options.insert(0,"All")
   spot_type=st.selectbox("Spot Type",options)

   max_distance =st.slider("Max Distance (km)",min_value=1,max_value=20,value=10)
   min_rating = st.slider("Min Rating",min_value=1.0,max_value=5.0,value=3.0,step=0.1)


   show_only_open =st.checkbox("Show only open spots",False)
   sort_by_location =st.radio("Sort By",["Distance","Rating"])

ss= df_areas[df_areas["label"]==selected_area][["lat","lng"]]
user_location=tuple(ss.iloc[0])

def get_row(row):
   return calculate_distance(user_location,row)

df["distance_km"] =df.apply(get_row,axis=1)
df["is_open"] =df.apply(is_open_spot,axis=1)

df2=df.copy()

if spot_type != "All":
   df=df[df["type"]==spot_type]

df=df[df["distance_km"]<= max_distance]
df= df[df["rating"]>=min_rating]

if show_only_open:
   df=df[df["is_open"]=="open"]

if sort_by_location=="Distance":
   df=df.sort_values(by="distance_km")
else:
   df =df.sort_values(by="rating",ascending=False)

if spot_name:
   df=df[df["name"].str.contains(spot_name,case=False)]

   
tab1,tab2,tab3=st.tabs(["🗺️ Nearby Spots","📊 Analytics","🏆 Leaderboard"])

with tab1:
   st.subheader(f"{len(df)} spot(s) found ☕️🍽️")
   dubai_map=folium.Map(location=user_location,zoom_start=13)
   marker_icon=folium.Icon(color="orange",icon="user")
   area_marker=folium.Marker(user_location,icon=marker_icon,tooltip=f"Area:{selected_area}")
   area_marker.add_to(dubai_map)
   
   for data in df.iterrows():
      row=data[1]
      lat=row["lat"]
      lng=row["lng"]
      name=row["name"]
      spot_type=row["type"]
      is_open =row["is_open"]
      color="green"
      if (is_open == "closed"):
         color= "red"


      spot_location=(lat,lng)
      m_icon=folium.Icon(color=color,icon="coffee",prefix="fa")
      marker=folium.Marker(spot_location,icon=m_icon,tooltip=f"{spot_type}:{name}")
      marker.add_to(dubai_map)
      
   st_folium(dubai_map,height=365,use_container_width=True)
   for i in range(0,len(df),2):
      small_df=df.iloc[i:i+2]
      columns=st.columns(2)
      for j in range(0,len(small_df)):
         with columns[j]:
            with st.container(border=True):
               row=small_df.iloc[j]
         
               spot_type=row["type"]
               icons=get_spot_icon(spot_type)
               st.subheader(f"{icons}{row["name"]}")

               
               col1,col2=st.columns(2)
               with col1:
                  st.markdown(f"###### type: {row["type"]}")
                  st.markdown(f"**Distance**:{row["distance_km"]}")
               with col2:
                  st.markdown(f"##### status: {row["is_open"]}")
                  rating=row["rating"]
                  st.markdown(f"##### rating:{"⭐️" *int(rating)}({rating})")
                  
               
   # st.dataframe(df)
with tab2:
   st.header("📈 Summary Stats")
   c1,c2,c3,c4=st.columns(4)
   total_spot=len(df2)
   avg_rating= round(df2["rating"].mean(),2)
   open_spot = len(df2[df2["is_open"]=="open"])
   sort_data= df2.sort_values(by="distance_km")
   min_dis=sort_data["distance_km"].iloc[0]
   c1.metric("Total Spots",total_spot)
   c2.metric("Avg Rating",avg_rating)
   c3.metric("Open Now",f"{open_spot}/{total_spot}")
   c4.metric("Nearest Spot",min_dis)

   st.subheader("📍Sopt Count By Type")
   spot_counts= df2["type"].value_counts()
   st.bar_chart(spot_counts)

   st.subheader("⭐️Average Rating by Type")
   avg_rating_spots=df2.groupby("type")["rating"].mean()
   st.bar_chart(avg_rating_spots,color="#F4EFB6")
   


with tab3:

 st.header("📈 Analytics & Ranking")
 st.subheader("🎯 Top 10 Rated Spots")
 top_rated_df =df2.sort_values(by="rating",ascending=False).reset_index(drop=True).head(10)
#  top_rated_df=top_rated_df.index + 1
 st.dataframe(top_rated_df[["name","type","rating","distance_km"]],hide_index=True)
 
 st.subheader("📍 Nearest 10 Spots to You")
 near_location_df=df2.sort_values(by="distance_km").reset_index(drop=True).head(10)

 st.dataframe(near_location_df[["name","type","rating","distance_km"]],hide_index=True)

   










