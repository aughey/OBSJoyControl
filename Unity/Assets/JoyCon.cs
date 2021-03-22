using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

class ValueFilter
{
    private readonly float alpha;
    float prev;

    public ValueFilter(float alpha)
    {
        this.alpha = alpha;
    }

    public float Filter(float value)
    {
        prev = value * alpha + (1.0f - alpha) * prev;
        return prev;
    }
}

public class JoyCon : MonoBehaviour
{
    // Rotation state
    public Vector2 lookDPS = new Vector2(90,90);
    public float look_exp = 2.0f;
    Vector2 stick_inputs;
    Vector3 integrated_rotation;

    // fov_base is the fov that is the "unity" fov where the movement
    // speeds are actual.  The movement speeds are scaled based on this
    // base fov.
    const float fov_base = 90.0f;

    // Zoom state
    public float zoom_filter_alpha = 0.1f;
    public float zoom_dps = 20.0f;
    float commanded_zoom_delta = 0.0f;

    ValueFilter zoom_filtered;

    // Start is called before the first frame update
    void Start()
    {
        zoom_filtered = new ValueFilter(zoom_filter_alpha);
    }

    public void OnLook(InputValue input)
    {
        stick_inputs = input.Get<Vector2>();
    }

    public void OnZoomIn(InputValue input)
    {
        commanded_zoom_delta = -input.Get<float>();
    }

    public void OnZoomOut(InputValue input)
    {
        commanded_zoom_delta = input.Get<float>();
    }

    float cameraFOV { 
        get => GetComponent<Camera>().fieldOfView; 
        set => GetComponent<Camera>().fieldOfView = value; 
    }

    static float RemapValue(float v, float exp)
    {
        return Mathf.Sign(v) * Mathf.Pow(Mathf.Abs(v), exp);
    }

    static Vector2 RemapStick(Vector2 stick, float exp)
    {
        return new Vector2(
            RemapValue(stick[0],exp),
            RemapValue(stick[1],exp)
            );
    }

    // Update is called once per frame
    private void FixedUpdate()
    {
        float dt = Time.fixedDeltaTime;

        float fovscale = Mathf.Tan(Mathf.Deg2Rad*cameraFOV/2) / Mathf.Tan(Mathf.Deg2Rad*fov_base/2);

        // Apply a power function to the stick inputs
        var commanded_speed = RemapStick(stick_inputs,look_exp) * lookDPS;

        var delta_rotation = commanded_speed * dt * fovscale;

        integrated_rotation[1] += delta_rotation[0];
        integrated_rotation[0] += -delta_rotation[1];

        transform.rotation = Quaternion.Euler(integrated_rotation);

        var actualzoom_delta = zoom_filtered.Filter(commanded_zoom_delta);

        float fov = cameraFOV;
        fov += actualzoom_delta * dt * zoom_dps * fovscale;
        fov = Mathf.Clamp(fov, 10.0f, 90.0f);
        cameraFOV = fov;
    }
}
