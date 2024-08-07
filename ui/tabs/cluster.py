import gradio as gr
# from clustering import grid_search, embeding ,clustering

# def cluster_tab():
#     with gr.Tab("이미지 클러스터링"):
#         with gr.Row():
#             with gr.Column(scale=0.2):
#                 df_bt = gr.Button("참고 테이블 생성")
#                 eps =  gr.Slider(0.01, 1, step = 0.01, value=0.5, label="epsilon", info="반경 몇까지 내 이웃 이미지인가")
#                 sample =  gr.Slider(1, 10, step = 1.0, value=3, label="min_sample", info="내 근처에 비슷한 이미지가 몇개 있어야 하는가")
#                 cl_bt = gr.Button("클러스터링 실행")

#             with gr.Column(scale=0.4):
#                 refresh_bt2 = gr.Button("시작전 반드시 클릭, 폴더 초기화")
#                 gen_list = gr.Gallery(label = "이미지들",elem_id="gallery", columns=[3], rows=[3])
#                 refresh_bt2.click(fn=load_images_from_folder_cluster, inputs =None, outputs = gen_list)
                
#             with gr.Column(scale=0.4):
#                 cluster_img_list = gr.Gallery(elem_id="clustering", columns=[1], rows=[1])

#         with gr.Row():
#             with gr.Column():
#                 gr.Markdown(""" ## [Clustering 결과 폴더](http://fb12.common12.deep.est.ai/files/docker/jsi6452_pipeline/first_work/Cluster/)     
#                                 - clustering_show : 원본 이미지, FS이미지, 2개를 합친 이미지들
#                                 - clustering_result : 클러스터링 결과물 중 대표 FS이미지
#                                 - clustering_pair : result+ origin = 2가지 결과물
#                                 - clustering_origin : 클러스터링 FS이미지의 원본 소스이미지
#                                 - clustering : 클러스터링 결과 이미지
#                             """, header_links = True) 
                
            
#                 df_gr = gr.Dataframe(row_count=[1 , 'fixed'] )
#                 df_bt.click(fn=grid_search, inputs = None, outputs = df_gr)

#         cl_bt.click(fn = clustering , inputs = [eps,sample], outputs = cluster_img_list)