{{- define "fiesta.secret" }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Args.Name | quote }}
  labels:
    {{- include "fiesta.labels" . | nindent 4 }}
data:
{{- $secretObj := (lookup "v1" "Secret" $.Release.Namespace .Args.Name) | default dict }}
{{- range $key, $value := .Args.Values }}
  {{- $secretData := (get $secretObj "data") | default dict }}
  {{/* set $key to existing secret data or generate a random one when not exists */}}
  {{- $outValue := (get $secretData $key) | default $value -}}
  {{ $key }}: {{ $outValue | quote }}
{{- end }}
{{- end }}
