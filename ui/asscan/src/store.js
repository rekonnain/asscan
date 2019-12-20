
/* eslint-disable no-console */

import Vuex from 'vuex'
export default new Vuex.Store({
    state: {
        currentIp: '',
        portFilter: '',
        prefixFilter: '',
        serviceFilter: '',
        vulns: false,
        screenshots: false,
    },

    getters: {
        currentIp: state => state.currentIp,
        portFilter: state => state.portFilter,
        prefixFilter: state => state.prefixFilter,
        vulns: state => state.vulns,
        screenshots: state => state.screenshots,
    },

    actions: {
        selectIp(context, value) {
            context.commit('setIp', value.ip)
        },
        setPort(context, value) {
            context.commit('setPort', value.port)
        },
        setPrefix(context, value) {
            context.commit('setPrefix', value.prefix)
        },
        setService(context, value) {
            context.commit('setService', value.service)
        },
        setVulns(context, value) {
            context.commit('setVulns', value.vulns)
        },
        setScreenshots(context, value) {
            context.commit('setScreenshots', value.screenshots)
        },
        refresh(context) {
            context.commit('refresh')
        }
    },


    mutations: {
        setIp(state, ip) {
            state.currentIp = ip;
        },
        setPort(state, port) {
            state.portFilter = port;
        },
        setPrefix(state, prefix) {
            state.prefixFilter = prefix;
        },
        setService(state, service) {
            state.serviceFilter = service;
        },
        setVulns(state, vulns) {
            state.vulns = vulns;
        },
        setScreenshots(state, screenshots) {
            state.screenshots = screenshots;
        },
        refresh() { }
    },
});
