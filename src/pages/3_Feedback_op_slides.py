from utils.utils_pptx import *

class FeedbackOpSlides:
    def __init__(self):
        pass

    def render_chart(self, score):
        bar_chart = alt.Chart(score).mark_bar().encode(x='Rubric', y='Score')
        st.altair_chart(bar_chart, use_container_width=True)
    
    @st.cache_data
    def load_PowerPoint(_self, uploaded_file):
        uploaded_file_bytes = uploaded_file.getvalue()
        uploaded_powerpoint = PowerPoint(uploaded_file_bytes)
        temp_dir_name = uploaded_powerpoint.save_uploaded_file()
        
        image_base64_list = uploaded_powerpoint.pptx_image_base64_list(os.path.join(temp_dir_name,'temp.pptx'), os.path.join(temp_dir_name,'temp.pdf'))
        feedback_list = uploaded_powerpoint.response_image_base64_list_openai("pptx_feedback", image_base64_list)

        score_list = uploaded_powerpoint.response_image_base64_list_openai("pptx_scores", image_base64_list)
        score_list = [ json_to_df(x, ["Rubric", "Score"]) for x in score_list ]
        return zip(image_base64_list, feedback_list, score_list)
    
    def render_scores(self, score):
        st.subheader("Evaluatie")
        st.markdown(score.to_html(index=False, classes='wide-table'), unsafe_allow_html=True)
        st.write("\n")
        total_score = score['Score'].sum() / 5
        st.subheader(f"Score: {total_score} / 5")

    
    def render_image(self, image_base64):
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        st.image(image, use_column_width=True)


    def run(self):
        st.title("Feedback op slides")
        uploaded_file = st.file_uploader("Upload a PowerPoint (*.pptx) file:", type='pptx')
        if uploaded_file is not None:
            zipped_list = self.load_PowerPoint(uploaded_file)
            
            left_column, right_column = st.columns([3, 1])
    
            st.markdown(
                """
                <style>
                .wide-table {
                    width: 100% !important;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            
            with right_column:
                st.title("Slides")
                for idx, (image_base64, feedback, score) in enumerate(zipped_list):
                    if st.button(f"Slide {idx + 1}", use_container_width=True):
                        with left_column:

                            self.render_image(image_base64)                            
                            st.markdown(feedback)

                            self.render_scores(score)
                            # self.render_chart(score)

if __name__ == "__main__":
    feedbackopslides = FeedbackOpSlides()
    feedbackopslides.run()