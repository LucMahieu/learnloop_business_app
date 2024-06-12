from utils.utils_pptx import *

class FeedbackOpSlides:
    def __init__(self):
        pass

    def run(self):
        st.query_params["phase"] = 3
        
        @st.cache_data
        def load_PowerPoint( uploaded_file):
            uploaded_file_bytes = uploaded_file.getvalue()
            uploaded_powerpoint = PowerPoint(uploaded_file_bytes)
            temp_dir_name = uploaded_powerpoint.save_uploaded_file()
            image_base64_list = uploaded_powerpoint.pptx_image_base64_list(os.path.join(temp_dir_name,'temp.pptx'),os.path.join(temp_dir_name,'temp.pdf'))
            feedback_list = uploaded_powerpoint.response_image_base64_list_openai("pptx_feedback", image_base64_list)
            score_list = uploaded_powerpoint.response_image_base64_list_openai("pptx_scores", image_base64_list)
            score_list = [ json_to_df(x, ["Rubric", "Score"]) for x in score_list ]
            return zip(image_base64_list, feedback_list, score_list)
        
        st.title("Feedback op slides verwerken")
        uploaded_file = st.file_uploader("Upload a PowerPoint (*.pptx) file:", type='pptx')
        if uploaded_file is not None:
            zipped_list = load_PowerPoint(uploaded_file)
            
            left_column, right_column = st.columns([3, 1])
    
            with right_column:
                st.title("Slides")
                for idx, (image_base64, feedback, score) in enumerate(zipped_list):
                    if st.button(f"Slide {idx + 1}"):
                        with left_column:
                            image_data = base64.b64decode(image_base64)
                            image = Image.open(BytesIO(image_data))
                            st.image(image, caption='Decoded from base64', use_column_width=True)
                            st.write(feedback)
                            st.write(score)
                            bar_chart = alt.Chart(score).mark_bar().encode(
                                x='Rubric',
                                y='Score')
                            st.altair_chart(bar_chart, use_container_width=True)

if __name__ == "__main__":
    feedbackopslides = FeedbackOpSlides()
    feedbackopslides.run()