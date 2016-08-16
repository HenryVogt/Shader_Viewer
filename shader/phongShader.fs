uniform vec4 ambientColor;
uniform vec4 diffuseColor;
uniform vec4 specularColor;
uniform sampler2D colorMap;
uniform bool texturize;

varying vec3 varyingLightDir;
varying vec3 varyingNormal;

float intensity(vec3 u, vec3 v)
{
	return float(max(0.0, dot(normalize(u), normalize(v))));
}

void main()
{
    float diff = intensity(varyingNormal, varyingLightDir);
    vec4 vFragColor = diff * diffuseColor;
    vFragColor += ambientColor;
    if (texturize == true)
    {
        vFragColor *= texture2D(colorMap, gl_TexCoord[0].st);
    }
    vec3 vReflect = normalize(reflect(-normalize(varyingLightDir), normalize(varyingNormal)));
    float spec = intensity(varyingNormal, vReflect);
    if (diff != 0.0)
    {
        float fSpec = pow(spec, 128.0);
        vFragColor.rgb += vec3(fSpec, fSpec, fSpec);
    }
    gl_FragColor = vFragColor;
}