{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "opendistro-es.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "opendistro-es.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}


{{/*
Define standard labels for frequently used metadata.
*/}}
{{- define "opendistro-es.labels.standard" -}}
app: {{ template "opendistro-es.fullname" . }}
chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
release: "{{ .Release.Name }}"
heritage: "{{ .Release.Service }}"
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "opendistro-es.kibana.serviceAccountName" -}}
{{- if .Values.kibana.serviceAccount.create -}}
    {{ default (include "opendistro-es.fullname" .) .Values.kibana.serviceAccount.name }}-kibana
{{- else -}}
    {{ default "default" .Values.kibana.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "opendistro-es.elasticsearch.serviceAccountName" -}}
{{- if .Values.elasticsearch.serviceAccount.create -}}
    {{ default (include "opendistro-es.fullname" .) .Values.elasticsearch.serviceAccount.name }}-es
{{- else -}}
    {{ default "default" .Values.elasticsearch.serviceAccount.name }}
{{- end -}}
{{- end -}}
