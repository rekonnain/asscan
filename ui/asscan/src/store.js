
/* eslint-disable no-console */

import Vuex from 'vuex'
export default new Vuex.Store({
    state: {
        currentIp: '',
        portFilter: '',
        prefixFilter: '',
        serviceFilter: '',
        contentFilter: '',
        vulns: false,
        screenshots: false,
        notes: false,
    },

    getters: {
        currentIp: state => state.currentIp,
        portFilter: state => state.portFilter,
        prefixFilter: state => state.prefixFilter,
        contentFilter : state => state.contentFilter,
        vulns: state => state.vulns,
        screenshots: state => state.screenshots,
        notes: state => state.notes,
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
        setContent(context, value) {
            context.commit('setContent', value.content)
        },
        setVulns(context, value) {
            context.commit('setVulns', value.vulns)
        },
        setScreenshots(context, value) {
            context.commit('setScreenshots', value.screenshots)
        },
        setNotes(context, value) {
            context.commit('setNotes', value.notes)
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
        setContent(state, content) {
            state.contentFilter = content;
        },
        setVulns(state, vulns) {
            state.vulns = vulns;
        },
        setScreenshots(state, screenshots) {
            state.screenshots = screenshots;
        },
        setNotes(state, notes) {
            state.notes = notes;
        },
        refresh() { }
    },
});
