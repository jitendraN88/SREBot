import os


import base64


def create_graph(title, xpoints, ypoints):
    imagepath = "/tmp/datatemp.png"
    import matplotlib.pyplot as plting
    plting.plot(xpoints, ypoints)
    plting.xlabel("Time")
    plting.ylabel("5xx Count")
    plting.legend()
    plting.title(title)
    figure = plting.gcf()
    figure.set_size_inches(10, 8)
    os.system("rm -rf {}".format(imagepath))
    plting.savefig(imagepath, dpi=100, bbox_inches='tight')
    graph_data_uri = create_data_URI(imagepath=imagepath)
    del plting
    return graph_data_uri
    # fig, ax = plt.subplots()
    # y_pos = xpoints
    # performance = ypoints
    #
    # ax.barh(y_pos, performance, align='center')
    # ax.set_yticks(y_pos, labels=y_pos)
    # ax.invert_yaxis()  # labels read top-to-bottom
    # ax.set_xlabel('5xx Error Count Stats')
    # ax.set_title(title)
    # plt.tight_layout()
    # plt.savefig(imagepath)


def create_data_URI(imagepath):
    binary_fc = open(imagepath, 'rb').read()  # fc aka file_content
    base64_utf8_str = base64.b64encode(binary_fc).decode('utf-8')
    dataurl = f'data:image/png;base64,{base64_utf8_str}'
    return dataurl
