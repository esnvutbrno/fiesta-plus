{{- define "fiesta.secret" }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Args.Name | quote }}
  labels:
    {{- include "fiesta.labels" . | nindent 4 }}
data:
{{- $secretObj := (lookup "v1" "Secret" $.Release.Namespace .Args.Name) | default dict }}
{{- range $key, $defaultValue := .Args.Values }}
  {{- $secretData := (get $secretObj "data") | default dict }}
  {{/* set $key to existing secret data or use default when not exists */}}
  {{- $value := (get $secretData $key) | default $defaultValue -}}
  {{ $key }}: {{ $value | quote }}
{{- end }}
{{- end }}
