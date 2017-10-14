using System.Linq;
using UnityEngine;

namespace Parabox.OD
{
	public static class MeshUtility
	{
		public static int[] TriangulatePolygon(int[] indices)
		{
			// for now just do a simple fan triangulate
			// in the future it would be nice to do ear clipping
			int[] triangles = new int[(indices.Length - 2) * 3];

			for (int i = 1; i < indices.Length - 1; i++)
			{
				triangles[(i-1)*3+0] = indices[0  ];
				triangles[(i-1)*3+1] = indices[i  ];
				triangles[(i-1)*3+2] = indices[i+1];
			}

			return triangles;
		}
	}
}