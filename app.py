import streamlit as st
#from streamlit_lottie import st_lottie
import pandas as pd
import numpy as np
from PIL import Image
import pickle
import json




def on_change_checkbox(movie_to_add, poster_to_add, plot_to_add, key) :
        
    if st.session_state['on_change_check' + str(key)] :
        
        st.session_state['watchlist'].append((movie_to_add, poster_to_add, plot_to_add, key))
        
    else:
        st.session_state['watchlist'].remove((movie_to_add, poster_to_add, plot_to_add, key))
    
    
    
    
def on_click_remove(movie_to_add, poster_to_add, plot_to_add, old_key, new_key) :
        
    st.session_state['watchlist'].remove((movie_to_add, poster_to_add, plot_to_add, old_key))
    
    st.session_state['on_change_check' + str(old_key)] = False
    
    del st.session_state['remove_list' + str(new_key)]



def initialize_session_state() :
    
    if 'limit' not in st.session_state :
        st.session_state['limit'] = 5
        
    if 'button' not in st.session_state :
        st.session_state['button'] = False
        
    if 'watchlist' not in st.session_state :
        st.session_state['watchlist'] = []
    
    
def change_limit() :
    
    if st.session_state['new_limit'] :
        
        st.session_state['limit'] = st.session_state['new_limit']
    
        
    
def load_lottiefile(filepath) :
    
    with open(filepath, "r") as f:
        return json.load(f)
        
        
@st.cache(show_spinner = False)
def load() :

    
    movies_list = pickle.load(open('movies.pkl', 'rb'))
    
    movies_df = pd.DataFrame(movies_list)
    
    cosine_sim = pickle.load(open('similarity.pkl', 'rb'))
    
    indices = pickle.load(open('indices.pkl', 'rb'))
        
    return movies_df, cosine_sim, indices





@st.cache(show_spinner = False)
def recommend(selected_movie, cosine_sim, indices, movies_df, original_language) :
    
    movie_idx = indices[selected_movie]
    
    index_list = list(movies_df[movies_df['original_language'] == original_language].index)
    
    sim_scores = np.array(list( enumerate(cosine_sim[movie_idx]) ), dtype = [('a', np.uint16), ('b', np.float32)])
    
    sim_scores = sim_scores[index_list]
        
    sim_scores = sorted(sim_scores, key = lambda score : score[1], reverse = True)
    
    sim_scores = sim_scores[1 : 16]

    movie_indices = [i[0] for i in sim_scores]
    
    
    recommended_movies = []
    recommended_movie_posters = []
    recommended_movie_plot = []
    
    for movie_info in movies_df.iloc[movie_indices].values :
        
        recommended_movies.append(movie_info[0])
        
        recommended_movie_posters.append(movie_info[3])
        
        recommended_movie_plot.append(movie_info[4])
        
    return recommended_movies, recommended_movie_posters, recommended_movie_plot, sim_scores


    

def display_recommended(recommendations, posters, plots) :
     
    for i in range(0, st.session_state['limit'], 5) :
        
        cols = st.columns(5, gap = "small")
        
        for j in range(0, 5) :
            
            cols[j].markdown('##')
            cols[j].markdown(f'##### {recommendations[i + j]}')
    
        cols = st.columns(5, gap = "small") 
        
        for j in range(0, 5) :
            
            with cols[j] : 
                
                
            
            
                with open("design.css") as d:
                
                    st.markdown(f"<style>{d.read()}</style>", unsafe_allow_html = True)
                
                    #st.markdown( f'<img src="{posters[i+j]}" class="grow" width="260" height="400" style="border-radius: 25px"><div class="g">{plots[i+j]}</div>', unsafe_allow_html = True)
                    
                    st.markdown( f"""
                                   <div class="container">
                                    <img src="{posters[i+j]}" class="image" width="260" height="400" style="border-radius: 25px">
                                        <div class="overlay">
                                        <div class="text">{plots[i+j]}</div>
                                    </div>
                                    </div>
                                
                                
                                
                                
                                
                                """, unsafe_allow_html = True)
            
    
                if 'on_change_check' + str(i+j) in st.session_state and st.session_state['on_change_check' + str(i+j)] :
                
                    st.checkbox('Add to watchlist', value = True, key = 'on_change_check' + str(i+j), on_change = on_change_checkbox, args = (recommendations[i+j], posters[i+j], plots[i+j], i+j))
                
                else:
                
                    st.checkbox('Add to watchlist', value = False, key = 'on_change_check' + str(i+j), on_change = on_change_checkbox, args = (recommendations[i+j], posters[i+j], plots[i+j], i+j))
            
                

def display_watchlist() :
    
    if len(st.session_state['watchlist']):
        
        for i in range(0,len(st.session_state['watchlist']), 5) :

            cols = st.columns(5, gap = "small")

            for j in range(0,5) :
            
                if len(st.session_state['watchlist']) > i+j :
                    cols[j].markdown('##')
                    cols[j].markdown(f'##### {st.session_state["watchlist"][i+j][0]}')
        
            cols = st.columns(5, gap = "small")

            for j in range(0,5) :

                if len(st.session_state['watchlist']) > i+j :
                    
                    
                
                    cols[j].markdown( f'<img src="{st.session_state["watchlist"][i+j][1]}" width="260" height="400" style="border-radius: 25px">', unsafe_allow_html = True)
                    cols[j].button('remove',key = 'remove_list' + str(i+j), on_click=on_click_remove, args = (st.session_state["watchlist"][i+j][0], st.session_state["watchlist"][i+j][1], st.session_state["watchlist"][i+j][2], st.session_state["watchlist"][i+j][3],i+j))
    
    
    else:
        
        st.markdown( '<p style="text-align:center;">Add movies to watchlist</p>', unsafe_allow_html = True)
        




def main():
    
    icon = Image.open('clapper.png')
    
    
    
    st.set_page_config(
        page_title = "Movie Recommender",
        page_icon = icon,
        layout = "wide" )
    
    movies_df, cosine_sim, indices = load()
        

    container1 = st.container()
    
    
    container1.markdown( '<h1 style="font-size:60px; text-align:center;">Movie Recommender</h1>', unsafe_allow_html = True)

    tab1,tab2 = st.tabs(["Recommend","Watchlist"])
    

    with tab1:
    
        container2 = st.container()
        
        

        selected_movie = container2.selectbox('Search a movie', list(movies_df['title']))
    
        movie_idx = indices[selected_movie]
    
        movie_searched = movies_df.iloc[movie_idx].values

        container3 = st.container()
        
        cols = container3.columns([1,1.5,1.5,1], gap="small")
    
        cols[1].image(movie_searched[3])
        
        with cols[2]:
            st.title(movie_searched[0])
            st.write(movie_searched[4])
            st.write('Year : ', movie_searched[1])
            st.write('Language : ', movie_searched[2])
        

        initialize_session_state()

        select = st.sidebar.selectbox("Select number of movies to display", options = (5,10,15), on_change = change_limit, key='new_limit')

        container4 = st.container()

        if container4.button('Recommend') or st.session_state['button'] :
        
            st.session_state['button'] = True
        
            recommendations, posters, plots, sim_scores = recommend(selected_movie, cosine_sim, indices, movies_df, movie_searched[2])
        
            display_recommended(recommendations, posters, plots)
        
        
        
        
    with tab2 :
    
        display_watchlist()
        
    st.markdown("""
                <style>
                .css-a3xrcd.egzxvld0
                {
                    visibility: hidden;
                }
                </style>
                """,unsafe_allow_html=True)
        

if __name__ == '__main__' : 
    
    
    
    main()




