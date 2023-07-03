
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


DATA_URL = (
    "C://Users//Usuario//Desktop//streamlit-nyc//streamlit-nyc//Motor_Vehicle_Collisions_-_Crashes.csv"
)
st.markdown(
    """
    <style>
    body {
        color: blue; /* Set text color to white */
        background-color: pink; /* Set background color to pink */
    }
/* Container for the parallax effect */
.parallax-container {
  height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
  perspective: 1px;
}


/* Content inside the parallax container */
.parallax-content {
  position: sticky;
  top: 0;
  height: 100vh;
  transform-style: preserve-3d;
  transform-origin: 0 0;
  will-change: transform;
}

/* Layers of the parallax effect */
.parallax-layer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* Example styling for different layers */
.parallax-layer.layer1 {
  transform: translateZ(-1px) scale(2);
}

.parallax-layer.layer2 {
  transform: translateZ(-2px) scale(3);
}

.parallax-layer.layer3 {
  transform: translateZ(-3px) scale(4);
}

/* Additional styling */
body {
  margin: 0;
  font-family: Arial, sans-serif;
}
    .css-fg4pbf {
  background-image: url('https://upload.wikimedia.org/wikipedia/commons/2/22/New_York_City_at_night_HDR.jpg');
        position: absolute;
        color: rgb(49, 51, 63);
        inset: 0px;
        overflow: hidden;
                background-color: yellow;

}
p, ol, ul, dl {
    margin: 0px 0px 1rem;
    padding: 0px;
    font-size: 1rem;
    font-weight: 400;
    background:  #ffff00;
}
.css-1dx1gwv {
    padding: 9.33333px 0px 0px;
    -webkit-box-pack: justify;
    justify-content: space-between;
    -webkit-box-align: center;
    align-items: center;
    display: flex;
    background:  #ffff00;
}
.st-b4 {
    display: flex;
    background:  #ffff00;
}
.css-15tx938 {
    font-size: 14px;
    color: rgb(49, 51, 63);
    margin-bottom: 0.5rem;
 
       height: auto;
    min-height: 1.5rem;
    vertical-align: middle;
    display: flex;
    flex-direction: row;
    -webkit-box-align: center;
    align-items: center;
    background:  #ffff00;
}

.css-10trblm {
    position: relative;
    flex: 1 1 0%;
    margin-left: calc(3rem);
        background: rgb(255, 255, 255);

}
    /* Modify the color of specific elements */
    .css-1g6gooi.e1wofg1y0 {
        color: blue; /* Set specific text color to green */
    }

    .css-1nqjr8p.e1wofg1y1 {
        background-color: pink; /* Set specific background color to blue */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Accidentes de autos en Nueva York") 
with open('C://Users//Usuario//Downloads//streami//styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.markdown('Esta aplicaci&oacute;n es un Dashboard que puede'
            'ser utilizada para analizar colisiones de autos en'
            'NYC🗽💥🚗')

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True)
    return data


data = {'latitude': [25.5]}

data = load_data(100000)

col1, col2, col3 = st.columns(3)


col1.markdown("""
    <style>
    .card {
        background-color: green;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

col2.markdown("""
    <style>
    .card {
        background-color: light-blue;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

col3.markdown("""
    <style>
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)


col1.markdown("""
    <div style="background-color: yellow; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <h3>Temperatura</h3>
        <p>20°F</p>
    </div>
    """, unsafe_allow_html=True)



col2.markdown("""
    <div style="background-color:  #ffff00; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <h3>Viento</h3>
        <p>9 mph</p>
    </div>
    """, unsafe_allow_html=True)


col3.markdown("""
    <div style="background-color: yellow; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <h3>Humedad</h3>
        <p>86%</p>
    </div>
    """, unsafe_allow_html=True)
st.header("Las personas m&aacute;s accidentadas de NY?")
injured_people = st.slider("Número de personas heridas en accidentes de auto", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("Cantidad de colisiones que ocurren en un tiempo dado del d&iacute;a")
hour = st.slider("Hora del Día", 0, 23)
original_data = data
data = data[data['date/time'].dt.hour == hour]

st.markdown("Colisiones de autos entre %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Colisiones de vehículos entre las %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Las 5 calles más peligrosas por clase de afectados")
select = st.selectbox('Clases Afectadas', ['Gente a pie', 'Ciclistas', 'Motorizados'])

if select == 'Gente a pie':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

elif select == 'Ciclistas':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw m')
    st.write(data)
