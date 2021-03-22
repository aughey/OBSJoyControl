using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using UnityEngine;

[ExecuteInEditMode]
public class RelativeComputer : MonoBehaviour
{
    public Transform other;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    public static Quaternion QuaternionFromMatrix(Matrix4x4 m)
    {
        // Adapted from: http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/index.htm
        Quaternion q = new Quaternion();
        q.w = Mathf.Sqrt(Mathf.Max(0, 1 + m[0, 0] + m[1, 1] + m[2, 2])) / 2;
        q.x = Mathf.Sqrt(Mathf.Max(0, 1 + m[0, 0] - m[1, 1] - m[2, 2])) / 2;
        q.y = Mathf.Sqrt(Mathf.Max(0, 1 - m[0, 0] + m[1, 1] - m[2, 2])) / 2;
        q.z = Mathf.Sqrt(Mathf.Max(0, 1 - m[0, 0] - m[1, 1] + m[2, 2])) / 2;
        q.x *= Mathf.Sign(q.x * (m[2, 1] - m[1, 2]));
        q.y *= Mathf.Sign(q.y * (m[0, 2] - m[2, 0]));
        q.z *= Mathf.Sign(q.z * (m[1, 0] - m[0, 1]));
        return q;
    }


    // Update is called once per frame
    void Update()
    {
        using UdpClient udpClient = new UdpClient("127.0.0.1", 5005);

        var m = transform.worldToLocalMatrix;
        
        //Debug.Log(m);
        //Debug.Log(other.localToWorldMatrix);

        m = m * other.localToWorldMatrix;

        //Debug.Log(m);

        var pos = m.GetColumn(3);
        pos = pos + new Vector4(0, 0, -1);
//        Debug.Log("Pos: " + pos);
        var q = QuaternionFromMatrix(m);
        var e = q.eulerAngles;
        //Debug.Log("Rot: " + e);

        var tosend = $"{e.x} {-e.y} {-e.z} {pos.x*100} {-pos.y*100} {-pos.z*100} {GetComponent<Camera>().fieldOfView}";
        var bytes = System.Text.Encoding.ASCII.GetBytes(tosend);

        udpClient.Send(bytes, bytes.Length);
    }
}
