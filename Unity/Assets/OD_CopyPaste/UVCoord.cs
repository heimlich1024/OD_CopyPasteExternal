using System;
using UnityEngine;

namespace Parabox.OD
{
	public struct UVCoord
	{
		public Vector2 position;
		public int polygonIndex;
		public int vertexIndex;

		public override string ToString()
		{
			return string.Format("{0} {1} {2}", position, polygonIndex, vertexIndex);
		}
	}
}