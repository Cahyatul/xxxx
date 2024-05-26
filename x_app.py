import streamlit as st
import requests
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup
import re
import nltk
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as SumyTokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

# Mengunduh tokenizer untuk bahasa Inggris (yang dapat digunakan untuk teks Indonesia)
nltk.download('punkt')

st.subheader('Selamat Datang Di Aplikasi Meringkas1', divider='rainbow')
st.write("Solusi Meringkas Cepat dijamin Akurat")

# Fungsi untuk mengambil teks dari URL
def get_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            article_text = ' '.join(p.get_text() for p in paragraphs)
            return article_text
        else:
            return f"Error: Status code {response.status_code}"
    except requests.RequestException as e:
        return f"Request failed: {e}"

# Fungsi untuk membersihkan teks
def clean_text(text):
    factory = StopWordRemoverFactory()
    stopword_remover = factory.create_stop_word_remover()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = stopword_remover.remove(text)
    return text

# Input Teks
text_input = st.text_area("Masukkan teks langsung di sini")

# Input URL
url_input = st.text_input("Masukkan URL artikel")

# Input File
uploaded_file = st.file_uploader("Unggah Dokumen (PDF atau DOCX)")

# Tombol Peringkas

if st.button('Lihat Teks'):
    text = ''
     if text_input:
        # Proses teks langsung
        text = text_input
         text = clean_text(text)
        st.session_state.text = text
        st.write(text)
    if url_input:
        # Proses URL
        text = get_text_from_url(url_input)
        text = clean_text(text)
        st.session_state.text = text
        st.write(text)
    elif uploaded_file:
        # Proses File
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            text = clean_text(text)
            st.session_state.text = text
            st.write(text)
        elif uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            text = ''
            for para in doc.paragraphs:
                text += para.text
            text = clean_text(text)
            st.session_state.text = text
            st.write(text)
        else:
            st.error('Format file tidak didukung.')
    else:
        st.error('Silakan masukkan URL atau unggah file.')

# Fungsi peringkas teks menggunakan TextRank
def summarize_text(text):
    parser = PlaintextParser.from_string(text, SumyTokenizer("english"))
    summarizer = TextRankSummarizer()
    summary = summarizer(parser.document, 3)  # Merangkum menjadi 3 kalimat
    return ' '.join([str(sentence) for sentence in summary])

# Tampilkan hasil peringkasan
if st.button('Tampilkan Ringkasan'):
    if 'text' in st.session_state:
        summary = summarize_text(st.session_state.text)
        st.write(summary)
    else:
        st.error('Silakan masukkan teks untuk diringkas.')
