#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd
import numpy as np
import datetime
from math import sin, cos, sqrt, atan2, radians


# #importation des donnees

# In[12]:


ticket_data=pd.read_csv('C:/Users/lol/Downloads/data/ticket_data.csv')
cities=pd.read_csv('C:/Users/lol/Downloads/data/cities.csv')
stations=pd.read_csv('C:/Users/lol/Downloads/data/stations.csv')
providers=pd.read_csv('C:/Users/lol/Downloads/data/providers.csv')

#Changer le format des dates dans les donnes a 'datetime' pour faciliter la manipulation des dates
# In[13]:


ticket_data['arrival_ts']=pd.to_datetime(ticket_data.arrival_ts)
ticket_data['departure_ts']=pd.to_datetime(ticket_data.departure_ts)
ticket_data['duree']=ticket_data['arrival_ts']-ticket_data['departure_ts']

#extraire les prix:min,max.mean, durees:min,max et la duree a partir des variables sum et count
# In[14]:


df=ticket_data.groupby(['o_city','d_city']).agg({'price_in_cents': ['min', 'max','mean'],'duree': ['min', 'max','sum','count']}).reset_index()
df[('duree','moyenne')]=df[('duree','sum')]/df[('duree','count')]
df=df.drop(columns=[('duree','sum'), ('duree','count')])

#joindre les tables ticket_data et cities pour extraires le nom des villes de depart et d'arrivee
nb:Nous avons defini un trajet a partir des villes de depart et d'arrivee
# In[15]:


df_o=df.join(cities[['unique_name','id']].set_index('id').add_suffix('_origine'),on='o_city')
df_d=df.join(cities[['unique_name','id']].set_index('id').add_suffix('_destination'),on='d_city')
df=df_o.merge(df_d)
df.columns = ['id_origine', 'id_destination', 'min_prix','max_prix','moy_prix','min_duree','max_duree'
              ,'moy_duree','name_o','name_d']

#Jointure de 'providers' avec la dataframe df  pour ajouter le type de transport a cette derniere
# In[27]:


df['transport_type']=ticket_data.join(providers[['id','transport_type']].set_index('id'),on='company')['transport_type']

#la fonction getDistanceFromLatLonInKm ci-dessous permet d'extraires les distances entre 
les villes des departs et des arrivees
# In[28]:


def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2):
    # approximate radius of earth in km
    R = 6373.0
    distance=[]
    for i in range(len(lat1)):
        dlon = lon2[i] - lon1[i]
        dlat = lat2[i] - lat1[i]
        a = sin(dlat / 2)**2 + cos(lat1[i]) * cos(lat2[i]) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance.append(R * c)
    return(distance)

#Jointure de 'cities' et de la dataframe df  pour ajouter la distance entre les villes a cette derniere
# In[29]:


d_o=df.join(cities[['id','latitude','longitude']].set_index('id'),on='id_origine')
d_d=df.join(cities[['id','latitude','longitude']].set_index('id'),on='id_destination')
df['distance']=getDistanceFromLatLonInKm(d_o['latitude'],d_o['longitude'],d_d['latitude'],d_d['longitude'])

#Ajouter le champ class_dist qui indique l'interval auquel appartient la distance entres les villes
# In[30]:


class_dist=[]
for i in df['distance']:
    if i<200:
        class_dist.append('0_200')
    elif np.logical_and(200< i, i<= 800):
        class_dist.append('201_800')
    elif np.logical_and(800< i, i<= 2000):
        class_dist.append('201_800')
    else:
        class_dist.append('2000_')
df['class_dist']=class_dist

#Grouper la dataframe selon l'interval auquel appartient la distance entre les villes de departs et 
d'arrivee puis selon le type de transport et afficher le prix moyen et la duree moyenne
# In[31]:


d1=df.groupby(['class_dist','transport_type']).agg({'moy_prix': ['mean'],'moy_duree': ['count','sum']})
d1[('moy_duree','moyenne')]=d1[('moy_duree','sum')]/d1[('moy_duree','count')]
d1=d1.drop(columns=[('moy_duree','sum'), ('moy_duree','count')])

