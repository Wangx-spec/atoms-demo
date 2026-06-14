{{- define "atoms.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "atoms.image" -}}
{{- printf "%s/%s:%s" .registry .image .tag -}}
{{- end -}}
