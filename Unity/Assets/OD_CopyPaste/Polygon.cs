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

		public Polygon(params int[] indices)
		{
			this.indices = indices;
		}

		public int[] GetTriangles()
		{
			return MeshUtility.TriangulatePolygon(indices);
		}
	}
}
