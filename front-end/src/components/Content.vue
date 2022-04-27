<template>
  <div id="Content">
    <el-dialog
      title="AI预测中"
      :visible.sync="dialogTableVisible"
      :show-close="false"
      :close-on-press-escape="false"
      :append-to-body="true"
      :close-on-click-modal="false"
      :center="true"
    >
      <el-progress :percentage="percentage"></el-progress>
      <span slot="footer" class="dialog-footer">请耐心等待约10秒钟</span>
    </el-dialog>

    <div id="CT"> 
      <div id="Table_image" style="margin-top: 20px ;font-size: 0">
        <el-radio-group v-model="radio1" size="medium" @change="openVn">
          <el-radio-button label="1" :plain="true" >Crowddet</el-radio-button>
          <el-radio-button label="2" :plain="true" >NOH NMS</el-radio-button>
        </el-radio-group>
      </div>
      <div id="CT_image" style="font-size: 0">
        <el-card
          id="CT_image_1"
          style="
            border-radius: 8px;
            width: 1200px;
            height: 500px;
            margin-bottom: -30px;
            margin-top: -20px;
          "
        >
        <div class="demo-image__preview1">
            <div
              v-loading="loading"
              element-loading-text="上传图片中"
              element-loading-spinner="el-icon-loading"
              style="width: 400px;height: 350px;"
            >
              <el-image
                :src="url_1"
                class="image_1"
                :preview-src-list="srcList"
                style="border-radius: 4px"
              >
                <div slot="error">
                  <div slot="placeholder" class="error">
                    <el-button
                      v-show="showbutton"
                      type="primary"
                      icon="el-icon-upload"
                      class="download_bt"
                      v-on:click="true_upload"
                    >
                      上传图像
                      <input
                        ref="upload"
                        style="display: none"
                        name="file"
                        type="file"
                        @change="update"
                      />
                    </el-button>
                  </div>
                </div>
              </el-image>
            </div>
            <div class="img_info_1" style="border-radius:  0 0 5px 5px">
              <span style="color: white; font-size:18px; letter-spacing: 6px">原始图像</span>
            </div>
        </div>
        <div class="demo-image__preview2">
            <div 
              v-loading="loading"
              element-loading-text="处理中,请耐心等待"
              element-loading-spinner="el-icon-loading"
              style="width: 400px;height: 350px;"
            >
              <el-image
                :src="url_2"
                class="image_1"
                :preview-src-list="srcList1"
                style="border-radius: 4px"
              >
                <div slot="error">
                  <div slot="placeholder" class="error">{{ wait_return }}</div>
                </div>
              </el-image>
            </div>
            <div class="img_info_1" style="border-radius:  0 0 5px 5px">
              <span style="color: white; font-size:18px; letter-spacing: 6px">检测结果</span>
            </div>
        </div>
        </el-card>
      </div>
      <div class="base_box" style="margin-top: 10px;">
        <!-- 卡片放置表格 -->
        <el-card style="border-radius: 8px">
          <div slot="header" class="clearfix">
            <span>检测目标</span>
            <el-button
              style="margin-left: 35px"
              v-show="!showbutton"
              type="primary"
              icon="el-icon-upload"
              class="download_bt"
              v-on:click="true_upload2"
            >
              重新选择图像
              <input
                ref="upload2"
                style="display: none"
                name="file"
                type="file"
                @change="update"
              />
            </el-button>
          </div>
          <el-tabs v-model="activeName">
            <el-tab-pane label="检测到的目标" name="first">
              <!-- 表格存放特征值 -->
              <el-table
                :data="feature_list"
                height="390"
                border
                style="width: 750px; text-align: center"
                v-loading="loading"
                element-loading-text="数据正在处理中，请耐心等待"
                element-loading-spinner="el-icon-loading"
                lazy
              >
                <el-table-column label="目标类别" width="250px">
                  <template slot-scope="scope">
                    <span>{{ scope.row[2] }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="目标大小" width="250px">
                  <template slot-scope="scope">
                    <span>{{ scope.row[0] }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="置信度" width="250px">
                  <template slot-scope="scope">
                    <span>{{ scope.row[1] }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Content",
  data() {
    return {
      server_url: "http://127.0.0.1:5003",
      activeName: "first",
      active: 0,
      centerDialogVisible: true,
      url_1: "",
      url_2: "",
      textarea: "",
      srcList: [],
      srcList1: [],
      feature_list: [],
      feature_list_1: [],
      feat_list: [],
      url: "",
      visible: false,
      wait_return: "等待上传",
      wait_upload: "等待上传",
      loading: false,
      table: false,
      isNav: false,
      showbutton: true,
      percentage: 0,
      fullscreenLoading: false,
      opacitys: {
        opacity: 0,
      },
      dialogTableVisible: false,
      radio1: 1
    };
  },
  created: function () {
    document.title = "毕业设计目标检测WEB端";
  },
  methods: {
    openVn() {
      //this.$createElement HTML写法 第一个为标签 第二个为参数 第三个为文本内容
      var net = {"data":this.radio1}
      let config = {
        headers: { "Content-Type": "application/json" },
      }; //添加请求头
      axios
        .post(this.server_url + "/net", net, config)
        .then((response) => {
          const h = this.$createElement;
          if (this.radio1 == 2){
            this.$message({
                message: h('p', null, [
                  h('span', null, ' 当前模型是 '),
                  h('i', { style: 'color: teal' }, 'NOH NMS')
                ])
                })
            }
          else if(this.radio1==1) {
            this.$message({
                message: h('p', null, [
                  h('span', null, ' 当前模型是 '),
                  h('i', { style: 'color: teal' }, 'Crowddet')
                ])
                });    
              }
          console.log(response);
        });     
    },

    true_upload() {
      this.$refs.upload.click();
    },
    true_upload2() {
      this.$refs.upload2.click();
    },
    next() {
      this.active++;
    },
    // 获得目标文件
    getObjectURL(file) {
      var url = null;
      if (window.createObjcectURL != undefined) {
        url = window.createOjcectURL(file);
      } else if (window.URL != undefined) {
        url = window.URL.createObjectURL(file);
      } else if (window.webkitURL != undefined) {
        url = window.webkitURL.createObjectURL(file);
      }
      return url;
    },
    // 上传文件
    update(e) {
      this.percentage = 0;
      this.dialogTableVisible = true;
      this.url_1 = "";
      this.url_2 = "";
      this.srcList = [];
      this.srcList1 = [];
      this.wait_return = "";
      this.wait_upload = "";
      this.feature_list = [];
      this.feat_list = [];
      this.fullscreenLoading = true;
      this.loading = true;
      this.showbutton = false;
      let file = e.target.files[0];
      this.url_1 = this.$options.methods.getObjectURL(file);
      let param = new FormData(); //创建form对象 表单
      param.append("file", file, file.name); //通过append向form对象添加数据
      var timer = setInterval(() => {
        this.myFunc();
      }, 300);
      let config = {
        headers: { "Content-Type": "multipart/form-data" },
      }; //添加请求头
      axios
        .post(this.server_url + "/upload", param, config)
        .then((response) => {
          this.percentage = 100;
          clearInterval(timer);
          this.url_1 = response.data.image_url;
          this.srcList.push(this.url_1);
          this.url_2 = response.data.draw_url;
          this.srcList1.push(this.url_2);
          this.fullscreenLoading = false;
          this.loading = false;

          this.feat_list = Object.keys(response.data.image_info);

          for (var i = 0; i < this.feat_list.length; i++) {
            response.data.image_info[this.feat_list[i]][2] = this.feat_list[i];
            this.feature_list.push(response.data.image_info[this.feat_list[i]]);
          }

          this.feature_list.push(response.data.image_info);
          this.feature_list_1 = this.feature_list[0];
          this.dialogTableVisible = false;
          this.percentage = 0;
          this.notice1();
          // console.log(response);
        });
    },
    //进度条
    myFunc() {
      if (this.percentage + 3 < 99) {
        this.percentage = this.percentage + 3;
      } else {
        this.percentage = 99;
      }
    },
    drawChart() {},
    notice1() {
      this.$notify({
        title: "预测成功",
        message: "点击图片可以查看大图",
        duration: 0,
        type: "success",
      });
    },
  },
  mounted() {
    this.drawChart();
  },
};
</script>

<style>
.el-button {
  padding: 12px 20px !important;
}

#hello p {
  font-size: 15px !important;
  /*line-height: 25px;*/
}


</style>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
.base_box{
  margin: 0 auto;
}

.text {
  font-size: 14px;
}


.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both;
}


.divider {
  width: 50%;
}

#CT {
  display: flex;
  height: 100%;
  width: 100%;
  flex-wrap: wrap;
  justify-content: center;
  margin: 0 auto;
  max-width: 1800px;
}

#CT_image_1 {
  width: 90%;
  height: 40%;
  margin: 0px auto;
  padding: 0px auto;
  margin-right: 80px;
  margin-left: 80px;
  margin-bottom: 0px;
  border-radius: 4px;
}

#CT_image {
  margin-bottom: 60px;
  margin-left: 30px;
  margin-right: 30px;
  margin-top: 30px;
}

.image_1 {
  width: 400px;
  height: 350px;
  background: #ffffff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.img_info_1 {
  height: 40px;
  width: 400px;
  text-align: center;
  background-color: #21b3b9;
  line-height: 30px;
}

.demo-image__preview1 {
  width: 250px;
  height: 450px;
  margin: 30px 100px;
  float: left;
}

.demo-image__preview2 {
  width: 250px;
  height: 450px;
  margin: 30px 205px;
  float: right;
  /* background-color: green; */
}

.error {
  margin: 150px auto;
  width: 50%;
  padding: 10px;
  text-align: center;
}

.block-sidebar {
  position: fixed;
  display: none;
  left: 50%;
  margin-left: 600px;
  top: 350px;
  width: 60px;
  z-index: 99;
}

.block-sidebar .block-sidebar-item {
  font-size: 50px;
  color: lightblue;
  text-align: center;
  line-height: 50px;
  margin-bottom: 20px;
  cursor: pointer;
  display: block;
}

div {
  display: block;
}

.block-sidebar .block-sidebar-item:hover {
  color: #187aab;
}

.download_bt {
  padding: 10px 16px !important;
}

#upfile {
  width: 104px;
  height: 45px;
  background-color: #187aab;
  color: #fff;
  text-align: center;
  line-height: 45px;
  border-radius: 3px;
  box-shadow: 0 0 2px 0 rgba(0, 0, 0, 0.1), 0 2px 2px 0 rgba(0, 0, 0, 0.2);
  color: #fff;
  font-family: "Source Sans Pro", Verdana, sans-serif;
  font-size: 0.875rem;
}

.file {
  width: 200px;
  height: 130px;
  position: absolute;
  left: -20px;
  top: 0;
  z-index: 1;
  -moz-opacity: 0;
  -ms-opacity: 0;
  -webkit-opacity: 0;
  opacity: 0; /*css属性&mdash;&mdash;opcity不透明度，取值0-1*/
  filter: alpha(opacity=0);
  cursor: pointer;
}

#upload {
  position: relative;
  margin: 0px 0px;
}

#Content {
  width: 85%;
  height: 800px;
  background-color: #ffffff;
  margin: 15px auto;
  display: flex;
  min-width: 1200px;
}

.divider {
  background-color: #eaeaea !important;
  height: 2px !important;
  width: 100%;
  margin-bottom: 50px;
}
.colortip {
    display: inline-block;
    height: 36px;
    line-height: 36px;
    font-size: 14px;
    color: #606266;
    font-weight: bold;
}

#Table_image {
  margin-bottom: 0px;
  margin-top: 0;
  margin-right: 300px;
  margin-left: 300px;
  height: 50px;
}


</style>


