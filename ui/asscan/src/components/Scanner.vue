<template>
  <div>
    <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
      <div class="">
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="masscan"
          v-on:change="changeHandler"
            v-model="values.masscan"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />masscan
        </div>

        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="nmap"
          v-on:change="changeHandler"
            v-model="values.nmap"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />nmap
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="ffuf"
          v-on:change="changeHandler"
            v-model="values.ffuf"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />ffuf
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="snmpwalk"
          v-on:change="changeHandler"
            v-model="values.snmp"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />snmpwalk
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="smbenum"
          v-on:change="changeHandler"
            v-model="values.smbenum"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />smb-enum
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="rdpscreenshot"
          v-on:change="changeHandler"
            v-model="values.rdp"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />rdp
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="webscreenshot"
          v-on:change="changeHandler"
            v-model="values.web"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />web
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="wappalyzer"
          v-on:change="changeHandler"
            v-model="values.wappalyzer"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />wappalyzer
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="vncscreenshot"
            v-model="values.vnc"
          v-on:change="changeHandler"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />VNC
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="bluekeep"
            v-model="values.bluekeep"
          v-on:change="changeHandler"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />Bluekeep
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="ms17_010"
            v-on:change="changeHandler"
            v-model="values.ms17_010"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />MS17-010
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="ms12_020"
            v-model="values.ms12_020"
          v-on:change="changeHandler"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />MS12-020
        </div>
        <div class="m-1 focus:outline-none focus:shadow-outline">
          <input
            type="checkbox"
            name="scantype"
            value="cve_2021_1675"
            v-model="values.cve_2021_1675"
          v-on:change="changeHandler"
            class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
          />CVE-2021-1675 aka Printnightmare
        </div>
      </div>

      <div class="mt-4 flex items-center justify-between">
        <label class="block text-gray-700 w-2/5 text-sm" for="username"
          >target</label
        >
        <label class="block text-gray-700 w-1/5 text-sm" for="netmask"
          >netmask</label
        >
        <label class="block text-gray-700 w-1/5 text-sm" for="port"
          >job max mask</label
        >
        <label class="block text-gray-700 w-1/5 text-sm" for="port">port</label>
      </div>
      <div class="flex items-center justify-between">
        <input
          class="shadow appearance-none border rounded w-2/5 py-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="target"
          type="text"
          v-model="values.target"
          v-on:input="changeHandler"
          placeholder="192.168.1.1"
        />
        <input
          class="shadow appearance-none border rounded w-1/5 mx-2 py-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="netmask"
          type="text"
          v-on:input="changeHandler"
          v-model="values.netmask"
          placeholder="16"
        />
        <input
          class="shadow appearance-none border rounded w-1/5 mx-2 py-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="port"
          type="text"
          v-on:input="changeHandler"
          v-model="values.splitmask"
          placeholder="24"
        />
        <input
          class="shadow appearance-none border rounded w-1/5 mx-2 py-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="port"
          type="text"
          v-on:input="changeHandler"
          v-model="values.port"
          placeholder="80"
        />
      </div>

      <div class="mt-4 flex items-center justify-between">
        <label class="block text-gray-700 w-2/5 text-sm" for="vncpassword"
          >VNC password</label
        >
        <label class="block text-gray-700 w-1/5 text-sm" for="domain"
          >Domain</label
        >
        <label class="block text-gray-700 w-1/5 text-sm" for="username"
          >Username</label
        >
        <label class="block text-gray-700 w-1/5 text-sm" for="password"
          >Password</label
        >
      </div>
      <div class="flex items-center justify-between">
        <input
          class="shadow appearance-none border rounded w-2/5 py-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="target"
          type="text"
          v-model="values.vncpassword"
          v-on:input="changeHandler"
          placeholder="hunter2 :D"
        />
        <input
          class="shadow appearance-none border rounded w-1/5 mx-2 py-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="netmask"
          type="text"
          v-model="values.domain"
          v-on:input="changeHandler"
          placeholder="MEGACORP"
        />
        <input
          class="shadow appearance-none border rounded w-1/5 mx-2 py-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="username"
          type="text"
          v-model="values.username"
          v-on:input="changeHandler"
          placeholder="Administrator"
        />
        <input
          class="shadow appearance-none border rounded w-1/5 mx-2 py-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="password"
          type="text"
          v-model="values.password"
          v-on:input="changeHandler"
          placeholder="makkara"
        />
      </div>



      <div class="mt-4 flex items-center">
        <label class="block text-gray-700 w-2/5 mx-2 px-1 text-sm" for="dchost"
          >Domain Controller address</label>
        <label class="block text-gray-700 w-1/5 mx-2 px-1 text-sm" for="masscanbitrate"
          >Masscan bitrate</label>
      </div>
      <div class="flex items-center">
        <input
          class="shadow appearance-none border rounded w-2/5 py-2 mx-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="dchost"
          type="text"
          v-model="values.dchost"
          v-on:input="changeHandler"
          placeholder="dc01.corp.com"
        />
        <input
          class="shadow appearance-none border rounded w-1/5 py-2 mx-2 px-1 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="masscanbitrate"
          type="text"
          v-model="values.masscanbitrate"
          v-on:input="changeHandler"
          placeholder="20000"
        />
      </div>



      <div class="mt-8 flex items-center justify-center">
        <input
          type="checkbox"
          name="scantype"
          value="smbenum"
          v-on:change="changeHandler"
          v-model="values.onlyfound"
          class="mr-2 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
        />Only scan discovered hosts
      </div>

      <div class="mt-8 flex items-center justify-center">
        <button
          class="py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          type="button"
          @click="submit()"
        >
          Submit
        </button>
      </div>
    </form>

    <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
      <code>{{values.curlcmdline}}</code>
    </div>

    <div v-if="scanlist.length > 0">
      <p>Nmap & masscan done so far:</p>
      <table class="table-auto">
        <tr
          class="odd:bg-green-200 even:bg-teal-200"
          v-for="scan in scanlist"
          :key="scan"
        >
          <td class="p-2">{{ scan["scantype"] }}</td>
          <td class="p-2">{{ scan["target"] }}</td>
          <td class="p-2">{{ scan["timestamp"] }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
/* eslint-disable no-console */
/* eslint-disable no-unused-vars */

import Vue from "vue";
import VueX from "vuex";
import VueRouter from "vue-router";
Vue.use(VueRouter);
Vue.use(VueX);
import axios from "axios";

export default {
  name: "Scanner",
  props: {
    scanlist: [],
  },
  data() {
    return {
      values: {
        target: "",
        netmask: "",
        splitmask: "",
        port: "",
        vncpassword: "",
        domain: "",
        username: "",
        password: "",
        dchost: "",
        masscan: false,
        nmap: false,
        ffuf: false,
        snmp: false,
        smbenum: false,
        rdp: false,
        web: false,
        wappalyzer: false,
        vnc: false,
        bluekeep: false,
        ms17_010: false,
        ms12_020: false,
        cve_2021_1675: false,
        onlyfound: false,
      },
    };
  },
  mounted() {
    this.getscans();
  },

  methods: {
    async post(url) {
      console.log("posting to " + url);
      const response = await axios.post(url);
      console.log("response:");
      console.log(response.data);
    },

    async getscans() {
      const scans = await axios.get("/api/scans/");
      console.log("scans");
      this.scanlist = scans.data["scans"];
      console.log(this.scanlist);
    },

    requestscan(scandescription) {
      let url = "/api/jobs/";
      console.log("scan description:");
      console.log(scandescription);
      axios.post(url, scandescription);
    },

    changeHandler(evt) {
        const that = this;
        console.log(this.createpayload());
        var cmdline = 'curl -H "Content-Type: application/json" -d \'' + JSON.stringify(this.createpayload()).replace('",', '", ') + '\' ' +  location.protocol + '//' + location.host + '/jobs/'
        this.values.curlcmdline = cmdline;
      },

    clearValues() {
        this.values.masscan = false;
        this.values.nmap = false;
        this.values.web = false;
        this.values.wappalyzer = false;
        this.values.rdp = false;
        this.values.vnc = false;
        this.values.snmp = false;
        this.values.smbenum = false;
        this.values.ffuf = false;
        this.values.bluekeep = false;
        this.values.ms17_010 = false;
        this.values.ms12_020 = false;
        this.values.cve_2021_1675 = false;
    },

    createpayload() {
      var payload = {};
      const netmask =
        this.values.netmask.length > 0 ? this.values.netmask : "32";

      payload.target = this.values.target;
      payload.mask = netmask;
      if (this.values.port.length > 0) {
        payload.port = this.values.port;
      }
      if (this.values.splitmask.length > 0) {
        payload.maxmask = this.values.splitmask;
      }
      if (this.values.vncpassword.length > 0) {
        payload.vncpassword = this.values.vncpassword;
      }
      if (this.values.domain.length > 0) {
        payload.domain = this.values.domain;
      }
      if (this.values.username.length > 0) {
        payload.username = this.values.username;
      }
      if (this.values.password.length > 0) {
        payload.password = this.values.password;
      }
      if (this.values.dchost.length > 0) {
        payload.dchost = this.values.dchost;
      }

      let scantypes = [];

      // curl -X POST 'http://localhost:8888/jobs/?prefix=10.20.20.85&type=snmpwalk'
      if (this.values.masscan) {
        scantypes.push("masscan");
      }
      if (this.values.nmap) {
        scantypes.push("nmap");
      }
      if (this.values.web) {
        scantypes.push("webscreenshot");
      }
      if (this.values.wappalyzer) {
        scantypes.push("wappalyzer");
      }
      if (this.values.rdp) {
        scantypes.push("rdpscreenshot");
      }
      if (this.values.vnc) {
        scantypes.push("vncscreenshot");
      }
      if (this.values.snmp) {
        scantypes.push("snmpwalk");
      }
      if (this.values.smbenum) {
        scantypes.push("smbenum");
      }
      if (this.values.ffuf) {
        scantypes.push("ffuf");
      }
      if (this.values.bluekeep) {
        scantypes.push("bluekeep");
      }
      if (this.values.ms17_010) {
        scantypes.push("ms17_010");
      }
      if (this.values.ms12_020) {
        scantypes.push("ms12_020");
      }
      if (this.values.cve_2021_1675) {
        scantypes.push("cve_2021_1675");
      }





      payload.scantypes = scantypes;
      payload.onlyfound = this.values.onlyfound;

      return payload;
      },

    submit() {
      if (this.values.target.length == 0) {
        alert("target field is empty, idiot");
        return;
      }

      if (this.values.port.length > 0) {
        const that = this;
        this.values.port.split(",").forEach(function(port) {
          const payload = that.createpayload();
          payload.port = port;
          console.log(payload);
          that.requestscan(payload);
        });
      } else {
        this.requestscan(this.createpayload());
      }
    },
  },
};
</script>
