<template>
  <div>
    <el-table
      v-loading="loading"
      :data="tableData.slice((currentPage-1)*pageSize,currentPage*pageSize)"
      stripe
      row-key="id"
      style="width: 100%"
      :expand-row-keys="expandKeys"
      @expand-change="expandChange"
    >
      <el-table-column type="expand">
        <template slot-scope="props">
          <el-form label-position="left" inline class="demo-table-expand">
            <el-form-item label="id">
              <span>{{ props.row.id }}</span>
            </el-form-item>
            <el-form-item label="c_guid">
              <span>{{ props.row.c_guid }}</span>
            </el-form-item>
            <el-form-item label="c_pid">
              <span>{{ props.row.c_pid }}</span>
            </el-form-item>
            <el-form-item label="c_sid">
              <span>{{ props.row.c_sid }}</span>
            </el-form-item>
            <el-form-item label="c_sdk_ver">
              <span>{{ props.row.c_sdk_ver }}</span>
            </el-form-item>
            <el-form-item label="c_prod_ver">
              <span>{{ props.row.c_prod_ver }}</span>
            </el-form-item>
            <el-form-item label="dev_ipv4">
              <span>{{ props.row.dev_ipv4 }}</span>
            </el-form-item>
            <el-form-item label="dev_mac">
              <span>{{ props.row.dev_mac }}</span>
            </el-form-item>
            <el-form-item label="is_extender_mac">
              <span>{{ props.row.is_extender_mac }}</span>
            </el-form-item>
            <el-form-item label="dev_brand">
              <span>{{ props.row.dev_brand }}</span>
            </el-form-item>
            <el-form-item label="brand_confidence">
              <span>{{ props.row.brand_confidence }}</span>
            </el-form-item>
            <el-form-item label="category_id">
              <span>{{ props.row.category_id }}</span>
            </el-form-item>
            <el-form-item label="category_class_id">
              <span>{{ props.row.category_class_id }}</span>
            </el-form-item>
            <el-form-item label="category_confidence">
              <span>{{ props.row.category_confidence }}</span>
            </el-form-item>
            <el-form-item label="dev_model">
              <span>{{ props.row.dev_model }}</span>
            </el-form-item>
            <el-form-item label="model_confidence">
              <span>{{ props.row.model_confidence }}</span>
            </el-form-item>
            <el-form-item label="hostname">
              <span>{{ props.row.hostname_1 }}</span>
            </el-form-item>
            <el-form-item label="hostname_confidence">
              <span>{{ props.row.hostname_1_confidence }}</span>
            </el-form-item>
            <el-form-item label="friendly_name">
              <span>{{ props.row.friendly_name }}</span>
            </el-form-item>
            <el-form-item label="friendly_name_rule">
              <span>{{ props.row.friendly_name_rule }}</span>
            </el-form-item>
            <el-form-item label="req_url">
              <span>{{ props.row.req_url }}</span>
            </el-form-item>
            <el-form-item label="log_date">
              <span>{{ props.row.log_date }}</span>
            </el-form-item>
            <el-form-item label="category_from" class="one-line">
              <span>{{ props.row.category_from }}</span>
            </el-form-item>
            <el-form-item label="category_from_ids" class="one-line">
              <span>{{ props.row.category_from_ids }}</span>
            </el-form-item>
            <el-form-item label="brand_from" class="one-line">
              <span>{{ props.row.brand_from }}</span>
            </el-form-item>
            <el-form-item label="brand_from_ids" class="one-line">
              <span>{{ props.row.brand_from_ids }}</span>
            </el-form-item>
            <el-form-item label="model_from" class="one-line">
              <span>{{ props.row.model_from }}</span>
            </el-form-item>
            <el-form-item label="model_from_ids" class="one-line">
              <span>{{ props.row.model_from_ids }}</span>
            </el-form-item>
          </el-form>
        </template>
      </el-table-column>

      <el-table-column prop="id" label="id"></el-table-column>
      <!-- <el-table-column prop="c_pid" label="c_pid"></el-table-column> -->
      <el-table-column prop="dev_ipv4" label="dev_ipv4"></el-table-column>
      <el-table-column prop="dev_mac" label="dev_mac"></el-table-column>
      <el-table-column prop="is_extender_mac" label="is_extender_mac"></el-table-column>
      <el-table-column prop="dev_brand" label="dev_brand"></el-table-column>
      <el-table-column prop="brand_confidence" label="brand_confidence"></el-table-column>
      <el-table-column prop="category_id" label="category_id"></el-table-column>
      <el-table-column prop="category_class_id" label="category_class_id"></el-table-column>
      <el-table-column prop="category_confidence" label="category_confidence"></el-table-column>
      <el-table-column prop="dev_model" label="dev_model"></el-table-column>
      <el-table-column prop="model_confidence" label="model_confidence"></el-table-column>
      <el-table-column prop="req_url" label="req_url"></el-table-column>
      <el-table-column prop="log_date" label="log_date"></el-table-column>
      <el-table-column label="Action">
        <template slot-scope="scope">
          <el-button-group>
            <el-button
              icon="el-icon-download"
              circle
              @click="Download(scope.row)"
              v-loading="scope.row.is_downloading"
            ></el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      :style="{'margin-top':'20px'}"
      background
      layout="total, sizes, prev, pager, next"
      :total="totalSize"
      :current-page="currentPage"
      :page-sizes="[7, 10, 12, 15]"
      hide-on-single-page
      @current-change="handleCurrentChange"
      @size-change="handleSizeChange"
    ></el-pagination>
  </div>
</template>

<script>
import { save_string, filter_json, filter_xml } from "./../utils/save";

export default {
  data() {
    return {
      loading: false,
      expandKeys: [],
      tableData: [],
      pageSize: 7,
      totalSize: 0,
      currentPage: 1
    };
  },
  mounted() {
    const pageSize = localStorage.getItem("pagesize");
    if (pageSize) {
      this.handleSizeChange(pageSize);
    }
  },
  methods: {
    setData(data) {
      this.tableData = [];
      this.currentPage = 1;
      for (var index in data) {
        this.$set(this.tableData, index, data[index]);
      }

      this.totalSize = this.tableData.length;
    },

    changeData(data) {
      for (var index in this.tableData) {
        if (this.tableData[index]["id"] === data["id"]) {
          let newData = this.tableData[index];
          for (var key in data) {
            newData[key] = data[key];
          }
          this.$set(this.tableData, index, newData);
        }
      }
    },

    handleCurrentChange(val) {
      this.currentPage = val;
    },

    handleSizeChange(val) {
      this.pageSize = val;
      localStorage.setItem("pagesize", val);
    },

    expandChange(row, expandedRows) {
      if (this.expandKeys.indexOf(row.id) >= 0) {
        this.expandKeys.shift();
        return;
      }

      if (row["category_from"] || row["brand_from"] || row["model_from"]) {
        return;
      }

      const postBody = {};
      postBody["id"] = row["id"];
      postBody["month"] = row["month"];
      postBody["server"] = row["server"];
      postBody["category_id"] = row["category_id"];
      postBody["dev_model"] = row["dev_model"];
      postBody["dev_brand"] = row["dev_brand"];

      this.loading = true;
      this.$http
        .post("from", postBody)
        .then(res => {
          this.loading = false;
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

          this.changeData(res["data"]["data"][0]);
          this.expandKeys.shift();
          this.expandKeys.push(row.id);
        })
        .catch(res => {
          this.$refs["result"].loading = false;
          this.showError(JSON.stringify(res, null, 2));
        });

      if (expandedRows.length > 1) {
        expandedRows.shift();
      }
    },

    Download(row) {
      row.is_downloading = true;
      this.changeData(row);

      this.$http
        .post("download", {
          s_guid: row["s_guid"],
          server: row["server"],
          s3_file_id: row["s3_file_id"]
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

          const filename = `${row.id}.${row.log_format}`;
          let content = res["data"]["data"][0];
          if (row.log_format == "json") {
            content = filter_json(content);
          } else {
            content = filter_xml(content);
          }

          save_string(filename, content);
          row.is_downloading = false;
          this.changeData(row);
        })
        .catch(res => {
          row.is_downloading = false;
          this.changeData(row);
          this.showError(JSON.stringify(res, null, 2));
        });
    },

    showError(msg) {
      this.$alert(`<p style="white-space: pre-wrap;">${msg}</p>`, "Error", {
        confirmButtonText: "OK",
        dangerouslyUseHTMLString: true
      });
    }
  }
};
</script>

<style>
.demo-table-expand {
  font-size: 0;
}
.demo-table-expand label {
  width: 170px;
  color: #99a9bf;
}
.demo-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 40%;
}

.one-line {
  color: #123123;
  width: 100% !important;
}
</style>