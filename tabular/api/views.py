import pandas as pd
import io
from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import seaborn as sns
import matplotlib.pyplot as plt
from ..models import DataSet
from .serializer import DataSetSerializer


class UploadFileView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DataSetSerializer

    @swagger_auto_schema(
        tags=["Data Management"],
        operation_description="Upload a CSV file to create a new dataset.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "file": openapi.Schema(
                    type=openapi.TYPE_FILE, description="CSV file to upload"
                ),
            },
            required=["file"],
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="File uploaded successfully",
                schema=DataSetSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: "No file provided or invalid file",
        },
    )
    def create(self, request, *args, **kwargs):
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]
        dataset = DataSet.objects.create(name=file.name, file=file)
        dataset.save()
        data = DataSetSerializer(dataset).data
        base_uri = request.build_absolute_uri().split("/api")[0]
        data["file"] = base_uri + data["file"]
        return Response(
            {
                "message": "File uploaded successfully",
                "data": data,
            },
            status=status.HTTP_201_CREATED,
        )


class GetDatasetView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DataSetSerializer

    @swagger_auto_schema(
        tags=["Data Management"],
        operation_description="Retrieve a dataset by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "dataset_id",
                openapi.IN_QUERY,
                description="ID of the dataset",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Dataset retrieved successfully",
                schema=DataSetSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: "Invalid dataset_id",
        },
    )
    def list(self, request, *args, **kwargs):
        data_set = DataSet.objects.filter(
            id=request.query_params.get("dataset_id")
        ).first()
        if data_set is None:
            return Response(
                {"error": "Invalid dataset_id"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(data_set)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateDatasetView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DataSetSerializer

    @swagger_auto_schema(
        tags=["Data Management"],
        operation_description="Update a dataset by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "dataset_id",
                openapi.IN_QUERY,
                description="ID of the dataset",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        request_body=DataSetSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Dataset updated successfully",
                schema=DataSetSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: "Invalid dataset_id",
        },
    )
    def update(self, request, *args, **kwargs):
        data_set = DataSet.objects.filter(
            id=request.data.get("dataset_id")
        ).first()
        if data_set is None:
            return Response(
                {"error": "Invalid dataset_id"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(instance=data_set, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteDatasetView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DataSetSerializer

    @swagger_auto_schema(
        tags=["Data Management"],
        operation_description="Delete a dataset by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "dataset_id",
                openapi.IN_QUERY,
                description="ID of the dataset",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            status.HTTP_200_OK: "Dataset deleted successfully",
            status.HTTP_400_BAD_REQUEST: "Invalid dataset_id",
        },
    )
    def destroy(self, request, *args, **kwargs):
        data_set = DataSet.objects.filter(
            id=request.query_params.get("dataset_id")
        ).first()
        if data_set is None:
            return Response(
                {"error": "Invalid dataset_id"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.serializer_class(instance=data_set)
        serializer.delete()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CalculateStatisticsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DataSetSerializer

    @swagger_auto_schema(
        tags=["Data Analysis"],
        operation_description="Calculate statistics (mean, median, mode, quartiles) for the dataset.",
        manual_parameters=[
            openapi.Parameter(
                "dataset_id",
                openapi.IN_QUERY,
                description="ID of the dataset",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Statistics calculated successfully",
                examples={
                    "application/json": {
                        "mean": {"column1": 10.5, "column2": 15.0},
                        "median": {"column1": 10.0, "column2": 14.5},
                        "mode": {"column1": 12, "column2": 14},
                        "quartiles": {
                            "0.25": {"column1": 8.0, "column2": 13.0},
                            "0.50": {"column1": 10.0, "column2": 14.5},
                            "0.75": {"column1": 12.5, "column2": 16.0},
                        },
                    }
                },
            ),
            status.HTTP_400_BAD_REQUEST: "Error processing the dataset or invalid dataset_id",
        },
    )
    def list(self, request, *args, **kwargs):
        try:
            dataset = DataSet.objects.get(id=request.query_params.get("dataset_id"))
            file_path = dataset.file.path
            df = pd.read_csv(file_path)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        statistics = {
            "mean": df.mean().to_dict(),
            "median": df.median().to_dict(),
            "mode": df.mode().iloc[0].to_dict(),
            "quartiles": df.quantile([0.25, 0.5, 0.75]).to_dict(),
        }
        return Response(statistics, status=status.HTTP_200_OK)


class PlotChartView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DataSetSerializer

    @swagger_auto_schema(
        tags=["Data Visualization"],
        operation_description="Generate a bar plot from the dataset.",
        manual_parameters=[
            openapi.Parameter(
                "dataset_id",
                openapi.IN_QUERY,
                description="ID of the dataset",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Chart generated successfully",
                examples={
                    "application/json": {
                        "message": "Chart created successfully",
                        "chart": "http://example.com/media/plot.png",
                    }
                },
            ),
            status.HTTP_400_BAD_REQUEST: "Error processing the dataset or invalid dataset_id",
        },
    )
    def list(self, request, *args, **kwargs):
        try:
            dataset = DataSet.objects.get(id=request.query_params.get("dataset_id"))
            df = pd.read_csv(dataset.file.path)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        plt.figure(figsize=(10, 6))
        sns.barplot(data=df)
        plt.savefig("media/plot.png")
        base_uri = request.build_absolute_uri().split("api")[0]
        chart = base_uri + "media/plot.png"
        return Response(
            {"message": "Chart created successfully", "chart": chart},
            status=status.HTTP_200_OK,
        )
# class DataSetViewSet(viewsets.ModelViewSet):
#     queryset = DataSet.objects.all()
#     serializer_class = DataSetSerializer
