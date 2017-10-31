using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Parabox.OD
{
	/**
	 * A path of vertex indices forming a polygon.
	 */
	public class Polygon
	{
		public int[] indices;
		public string material;

		public Polygon(string material, params int[] indices)
		{
			this.material = material;
			this.indices = indices;
		}

		public int[] GetTriangles()
		{
			return MeshUtility.TriangulatePolygon(indices);
		}
	}
}
