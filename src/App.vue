<template>
  <el-container>
    <vue-canvas-nest :config="{color:'26,115,232', count: 150}" ></vue-canvas-nest>
    <el-header>Welcome to DR Log Check System</el-header>
    <el-container>
      <el-aside width="300px" style="margin-top: 20px;">
        <el-card class="box-card">
          <el-form
            :model="formDeviceID"
            label-position="left"
            label-width="86px"
            class="demo-ruleForm"
            size="mini"
          >
            <el-form-item label="ID / Mac">
              <el-input v-model="formDeviceID.query" placeholder="ID / Mac" @keyup.enter.native="checkByDeviceID"></el-input>
            </el-form-item>

            <el-form-item label="GUID / GW">
              <el-input v-model="formDeviceID.c_query" placeholder="GUID / Gateway Mac" @keyup.enter.native="checkByDeviceID"></el-input>
            </el-form-item>

            <el-form-item label="Server">
              <el-select v-model="formDeviceID.server" placeholder="Server">
                <el-option label="Prod" value="Prod"></el-option>
                <el-option label="Beta" value="Beta"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="Month">
              <el-select v-model="formDeviceID.month" placeholder="Month">
                <div v-for="item in monthList" :key="item.key">
                  <el-option :label="item.label" :value="item.value"></el-option>
                </div>
              </el-select>
            </el-form-item>

            <el-form-item label="Protocol">
              <el-select v-model="formDeviceID.protocol" placeholder="Protocol">
                <div v-for="item in protocolList" :key="item.key">
                  <el-option :label="item.label" :value="item.value"></el-option>
                </div>
              </el-select>
            </el-form-item>

            <el-form-item label="Date">
              <el-date-picker
                v-model="formDeviceID.date"
                type="date"
                value-format="yyyy-MM-dd"
                placeholder="Choose Date"
                :style="{'width': 'auto'}"
              ></el-date-picker>
            </el-form-item>

            <el-form-item label="log_date">
              <el-radio-group v-model="formDeviceID.log_date">
                <el-radio label="desc"></el-radio>
                <el-radio label="asc"></el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="checkByDeviceID" v-loading="isSearching">Search</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="box-card" v-if="false">
          <el-form
            :model="formDefpwd"
            label-position="left"
            label-width="80px"
            class="demo-ruleForm"
            size="mini"
          >
            <el-form-item label="ID">
              <el-input v-model="formDefpwd.id" placeholder="ID"></el-input>
            </el-form-item>

            <el-form-item label="Server">
              <el-select v-model="formDefpwd.server" placeholder="Server">
                <el-option label="Prod" value="Prod"></el-option>
                <el-option label="Beta" value="Beta"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="Month">
              <el-input v-model="formDefpwd.month" placeholder="ID"></el-input>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="downloadPwd">Search</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-aside>

      <el-main>
        <el-card class="box-card">
          <log-list ref="result"></log-list>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import vueCanvasNest from 'vue-canvas-nest'
import LogList from "./components/LogList";
import { save_string, filter_json } from "./utils/save";
export default {
  components: {
    LogList,
    vueCanvasNest
  },
  data() {
    return {
      monthList: [
        {
          label: "ALL",
          value: "ALL"
        }
      ],
      protocolList: [
        {
          label: "ALL",
          value: ""
        },
        {
          label: "openports",
          value: "/api/json/openports"
        },
        {
          label: "mac",
          value: "/api/json/mac"
        },
        {
          label: "services",
          value: "/api/json/services"
        },
        {
          label: "multiwsdd",
          value: "/api/json/multiwsdd"
        },        
        {
          label: "useragent",
          value: "/api/json/useragent"
        },
        {
          label: "multiupnp",
          value: "/api/json/multiupnp"
        },
        {
          label: "multimdns",
          value: "/api/json/multimdns"
        },   
        {
          label: "installdevice",
          value: "/api/json/installdevice"
        },          
        {
          label: "sniffdns",
          value: "/api/json/sniffdns"
        },
        {
          label: "multidhcp",
          value: "/api/json/multidhcp"
        },
        {
          label: "multihostname",
          value: "/api/json/multihostname"
        },
        {
          label: "homepage",
          value: "/api/json/homepage"
        },
        {
          label: "namp_log",
          value: "/api/log"
        }
      ],
      formDeviceID: {
        id: "",
        server: "Prod",
        month: "ALL",
        date: "",
        log_date: "desc",
        protocol: "ALL"
      },
      formDefpwd: {
        query: "",
        server: "Prod",
        month: "06"
      },
      isSearching: false
    };
  },
  methods: {
    checkByDeviceID() {
      if (this.isSearching) {
        return;
      }

      if (!this.formDeviceID.query && !this.formDeviceID.c_query) {
        this.$message({
          message: "Please fill the query condition",
          type: "warning"
        });
        return;
      }

      this.$refs["result"].loading = true;
      this.isSearching = true;
      this.$http
        .post("log", this.formDeviceID)
        .then(res => {
          this.$refs["result"].loading = false;
          this.isSearching = false;
          if (res["data"]["code"] != 0) {
            this.showError(res["data"]["msg"]);
            return;
          }

          if (res["data"]["data"].length === 0) {
            this.$message({
              message: "No Result Found",
              type: "warning"
            });
          }

          this.$refs["result"].setData(res["data"]["data"]);
        })
        .catch(res => {
          this.$refs["result"].loading = false;
          this.isSearching = false;
          this.showError(JSON.stringify(res, null, 2));
        });
    },

    downloadPwd() {
      this.$http
        .post("pwd", {
          id: this.formDefpwd.id,
          server: this.formDefpwd.server,
          month: this.formDefpwd.month
        })
        .then(res => {
          if (res["data"]["code"] != 0) {
            this.showError(res["data"]["msg"]);
          }

          if (res["data"]["data"].length === 0) {
            this.$message({
              message: "No Log Found",
              type: "warning"
            });
          }

          const filename = `${this.formDefpwd.id}.json`;
          let content = res["data"]["data"][0]["$"];
          content = filter_json(content);
          save_string(filename, content);
        })
        .catch(res => {
          this.showError(JSON.stringify(res, null, 2));
        });
    },

    initMonth() {
      this.$http
        .get("month")
        .then(res => {
          const data = res["data"];
          if (data["code"] != 0) {
            this.showError(data["msg"]);
            return;
          }

          data["data"].forEach(item => {
            let label = `20${item.slice(1, 3)}-${item.slice(4, 6)}`;
            this.monthList.push({
              label: label,
              value: item
            });
          });
        })
        .catch(res => {
          this.showError(JSON.stringify(res, null, 2));
        });
    },

    showError(msg) {
      this.$alert(`<p style="white-space: pre-wrap;">${msg}</p>`, "Error", {
        confirmButtonText: "OK",
        dangerouslyUseHTMLString: true
      });
    }
  },
  mounted() {
    this.initMonth();
  }
};
</script>

<style>
body {
  font-family: Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB,
    Microsoft YaHei, SimSun, sans-serif;
  font-weight: 400;
}

.el-header,
.el-footer {
  color: #333;
  text-align: center;
  font-weight: bold;
  line-height: 60px;
}

.el-aside {
  color: #333;
}
</style>
