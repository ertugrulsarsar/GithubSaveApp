"""Gelişmiş GitHub API Veri Toplama ve Analiz Aracı"""
import streamlit as st
import requests
import json
import pandas as pd
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from collections import Counter
import time

# Sayfa yapılandırması
st.set_page_config(
    page_title="GitHub Repo Analiz Aracı",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile görünümü özelleştirme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0366d6;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2ea44f;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .card {
        background-color: #f6f8fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e1e4e8;
    }
    .highlight {
        color: #0366d6;
        font-weight: bold;
    }
    .info-text {
        color: #586069;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Başlık ve açıklama
st.markdown('<div class="main-header">GitHub Repo Analiz Aracı</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-text">
Bu uygulama, GitHub kullanıcılarının repolarını analiz eder ve çeşitli istatistikler sunar.
Kullanıcı adını girerek başlayın.
</div>
""", unsafe_allow_html=True)

# Sidebar bilgileri
with st.sidebar:
    st.markdown("### Uygulama Hakkında")
    st.markdown("""
    Bu uygulama şunları yapar:
    - Kullanıcının tüm repolarını listeler
    - En çok yıldız alan repoları gösterir
    - En son güncellenen repoları gösterir
    - Programlama dillerine göre analiz yapar
    - Verileri JSON ve Pickle formatında kaydeder
    """)
    
    st.markdown("### Geliştirici Bilgileri")
    st.markdown("GitHub Repo Analiz Aracı © 2025")

# Ana içerik
col1, col2 = st.columns([2, 1])

with col1:
    username = st.text_input("GitHub Kullanıcı Adı:", placeholder="Örn: user123")

# Kullanıcı adı girildiğinde
if username:
    # API isteği ve veri alımı
    with st.spinner(f"{username} kullanıcısının repoları yükleniyor..."):
        url = f"https://api.github.com/users/{username}/repos"
        user_url = f"https://api.github.com/users/{username}"
        
        # Kullanıcı bilgilerini al
        user_response = requests.get(user_url)
        
        # Repo bilgilerini al
        response = requests.get(url)
        
    if response.status_code == 200 and user_response.status_code == 200:
        repos = response.json()
        user_info = user_response.json()
        
        # Kullanıcı profil bilgileri
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(user_info["avatar_url"], width=100)
            with cols[1]:
                st.markdown(f"### [{username}]({user_info['html_url']})")
                st.markdown(f"Takipçi: {user_info['followers']} | Takip Edilen: {user_info['following']}")
                if user_info["bio"]:
                    st.markdown(f"Bio: {user_info['bio']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Genel istatistikler
        st.markdown('<div class="sub-header">Genel İstatistikler</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Toplam Repo Sayısı", len(repos))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            # En çok yıldıza sahip repo
            max_star_repo = max(repos, key=lambda x: x["stargazers_count"]) if repos else None
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if max_star_repo:
                st.metric("En Çok Yıldız", max_star_repo["stargazers_count"], 
                          help=f"Repo: {max_star_repo['name']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            # En son güncellenen repo
            last_update_repo = max(repos, key=lambda x: datetime.strptime(x["updated_at"], "%Y-%m-%dT%H:%M:%SZ")) if repos else None
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if last_update_repo:
                update_date = datetime.strptime(last_update_repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y")
                st.metric("Son Güncelleme", update_date, 
                          help=f"Repo: {last_update_repo['name']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            # Toplam fork sayısı
            total_forks = sum(repo["forks_count"] for repo in repos)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Toplam Fork", total_forks)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Sekme oluşturma
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Repo Listesi", "⭐ Yıldız Sıralaması", "🔤 Dil Analizi", "📅 Güncelleme Sıralaması"])
        
        with tab1:
            # Repo listesi
            if repos:
                repo_df = pd.DataFrame([{
                    "Repo Adı": repo["name"],
                    "Açıklama": repo["description"] if repo["description"] else "-",
                    "Yıldız": repo["stargazers_count"],
                    "Fork": repo["forks_count"],
                    "Dil": repo["language"] if repo["language"] else "Belirtilmemiş",
                    "Son Güncelleme": datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y"),
                    "URL": repo["html_url"]
                } for repo in repos])
                
                st.dataframe(
                    repo_df,
                    column_config={
                        "Repo Adı": st.column_config.TextColumn("Repo Adı"),
                        "URL": st.column_config.LinkColumn("GitHub Linki")
                    },
                    use_container_width=True,
                    hide_index=True
                )
        
        with tab2:
            # Yıldız sıralaması
            sorted_repos = sorted(repos, key=lambda x: x["stargazers_count"], reverse=True)
            
            if sorted_repos:
                # Yıldız grafiği
                top_repos = sorted_repos[:10]  # En çok yıldıza sahip 10 repo
                
                fig = px.bar(
                    x=[repo["name"] for repo in top_repos],
                    y=[repo["stargazers_count"] for repo in top_repos],
                    labels={"x": "Repo Adı", "y": "Yıldız Sayısı"},
                    title="En Çok Yıldıza Sahip Repolar",
                    color=[repo["stargazers_count"] for repo in top_repos],
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Yıldız tablosu
                star_df = pd.DataFrame([{
                    "Repo Adı": repo["name"],
                    "Yıldız": repo["stargazers_count"],
                    "URL": repo["html_url"]
                } for repo in sorted_repos])
                
                st.dataframe(
                    star_df,
                    column_config={
                        "URL": st.column_config.LinkColumn("GitHub Linki")
                    },
                    use_container_width=True,
                    hide_index=True
                )
        
        with tab3:
            # Dil analizi
            languages = [repo["language"] for repo in repos if repo["language"] is not None]
            language_count = Counter(languages)
            
            if language_count:
                # Dil pasta grafiği
                fig = px.pie(
                    values=list(language_count.values()),
                    names=list(language_count.keys()),
                    title="Programlama Dilleri Dağılımı",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Dil tablosu
                lang_df = pd.DataFrame({
                    "Programlama Dili": list(language_count.keys()),
                    "Repo Sayısı": list(language_count.values())
                })
                
                st.dataframe(
                    lang_df.sort_values("Repo Sayısı", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
        
        with tab4:
            # Güncelleme sıralaması
            sorted_by_update = sorted(repos, key=lambda x: datetime.strptime(x["updated_at"], "%Y-%m-%dT%H:%M:%SZ"), reverse=True)
            
            if sorted_by_update:
                # Güncelleme zaman çizelgesi
                update_df = pd.DataFrame([{
                    "Repo": repo["name"],
                    "Başlangıç Tarihi": datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
                    "Güncelleme Tarihi": datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                } for repo in sorted_by_update[:10]])  # Son 10 güncelleme
                
                fig = px.timeline(
                    update_df, 
                    x_start="Başlangıç Tarihi", 
                    x_end="Güncelleme Tarihi",
                    y="Repo",
                    title="Repo Zaman Çizelgesi (Oluşturma - Son Güncelleme)"
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)
                
                # Güncelleme tablosu
                update_table_df = pd.DataFrame([{
                    "Repo Adı": repo["name"],
                    "Oluşturma Tarihi": datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y"),
                    "Son Güncelleme": datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y %H:%M"),
                    "URL": repo["html_url"]
                } for repo in sorted_by_update])
                
                st.dataframe(
                    update_table_df,
                    column_config={
                        "URL": st.column_config.LinkColumn("GitHub Linki")
                    },
                    use_container_width=True,
                    hide_index=True
                )
        
        # Veri kaydetme bölümü
        st.markdown('<div class="sub-header">Verileri Kaydet</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.button("JSON Olarak Kaydet"):
                with open(f"{username}_repos.json", "w") as file:
                    json.dump(repos, file)
                st.success(f"{username}_repos.json dosyası oluşturuldu.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.button("Pickle Olarak Kaydet"):
                with open(f"{username}_repos.pkl", "wb") as file:
                    pickle.dump(repos, file)
                st.success(f"{username}_repos.pkl dosyası oluşturuldu.")
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.error(f"Kullanıcı bulunamadı veya GitHub API'ye erişim sırasında bir hata oluştu. (Hata Kodu: {response.status_code})")
        if response.status_code == 403:
            st.warning("GitHub API istek limiti aşılmış olabilir. Lütfen daha sonra tekrar deneyin.")
        
else:
    # Kullanıcı adı girilmediğinde gösterilecek içerik
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.info("👆 Lütfen GitHub kullanıcı adı girerek başlayın.")
    st.markdown("""
    Bu uygulama ile:
    - Kullanıcının tüm repolarını görüntüleyebilir
    - En çok yıldız alan repoları analiz edebilir
    - Programlama dili dağılımını görebilir
    - Repo güncelleme geçmişini inceleyebilirsiniz
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Örnek görsel
    st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=200)


